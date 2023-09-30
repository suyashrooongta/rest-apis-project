from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError

from models import TagModel, StoreModel, ItemModel
from db import db
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("Tags", __name__, description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        return StoreModel.query.get_or_404(store_id).tags.all()


    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if (TagModel.query.filter(TagModel.store_id == store_id and TagModel.name == tag_data["name"])).first():
            abort(400, message="A tag with that name already exists in that store.")
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        return TagModel.query.get_or_404(tag_id)
    
    @blp.response(202, description="Deletes a tag if no item is tagged with it.", example={"message": "Tag deleted."})
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        else:
            abort(400, message="Tag not deleted since it is assigned to one or more items.")

    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while linking the tag.")

        return tag
    
    
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        if tag in item.tags:
            item.tags.remove(tag)
            try:
                db.session.add(item)
                db.session.commit()
                return {"message": "Item removed from tag", "item": item, "tag": tag}
            except SQLAlchemyError:
                abort(500, message="An error occured while linking the tag.")
        else:
            abort(400, message="Item not linked with tag.")


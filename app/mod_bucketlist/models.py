from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from app.models import Base
from app.mod_auth.models import UserAccount
from sqlalchemy.orm import relationship
import json


class BucketList(Base):
    """Maps to the bucketlists table """
    __tablename__ = 'bucketlists'
    name = Column(String(256), nullable=False)
    created_by = Column(Integer, ForeignKey(UserAccount.id))

    user = relationship('UserAccount')
    items = relationship('BucketListItem')

    def __init__(self, created_by, name):
        """ Initialize with the creator and name of bucketlist """
        self.created_by = created_by
        self.name = name

    @staticmethod
    def get_all(user_id):
        """Returns logged in user bucketlist data """
        return BucketList.query.filter_by(created_by=user_id)

    def __repr__(self):
        return "Id: {}, name: {}, created_by: {}".format(self.id, self.name, self.created_by)

    def to_json(self):
        return dict(
            id=self.id,
            name=self.name,
            created_by=self.created_by,
            date_created=self.date_created,
            date_modified=self.date_modified
        )

    def from_json(self, bucket_list):
        bucketlist = json.loads(bucket_list)
        self.name = bucketlist["name"]
        self.created_by = bucketlist["created_by"]


class BucketListItem(Base):
    """ Maps to BucketList table """
    __tablename__ = 'bucketlist_items'
    name = Column(String(256), nullable=False, unique=True)
    done = Column(Boolean, default=False)
    bucketlist_id = Column(Integer, ForeignKey(BucketList.id))

    def __init__(self, bucketlist_id, name, done=False):
        """Initializes model with id,name,done defaulting to False """
        self.name = name
        self.done = False if done else False
        self.bucketlist_id = bucketlist_id

    def update(self, **kwargs):
        """Updates the object instance of the model """
        self.name = kwargs.get('name')
        if kwargs.get('done') == 'True' or kwargs.get('done') == 'true':
            self.done = True
        else:
            self.done = False
        db.session.commit()

    def __repr__(self):
        return "Id: {}, bucketlist_id: {}, name: {}, done: {}".format(self.id, self.bucketlist_id, self.name, self.done)

    def to_json(self):
        return dict(
            id=self.id,
            bucketlist_id=self.bucketlist_id,
            name=self.name,
            done=self.done,
        )

    def from_json(self, bucketlist_item):
        bucketlistitem = json.loads(bucketlist_item)
        self.bucketlist_id = bucketlistitem["id"]
        self.name = bucketlistitem["name"]
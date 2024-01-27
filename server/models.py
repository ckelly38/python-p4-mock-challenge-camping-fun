from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class MyValidator:
    def __init__(self):
        self.disablevalidator = False;

    def strValHasAtMinXChars(self, val, x):
        if (type(x) == int): pass;
        else: raise ValueError("x must be an integer!");
        if (x < 0): raise ValueError("x must not be less than zero!");
        if (self.disablevalidator): return True;
        if (x < 1):
            if (val == None): return True;
            elif (type(val) == str): return True;
            else: raise ValueError("val must be a string!");
        else:
            if (val == None): return False;
            elif (type(val) == str): return (not(len(val) < x));
            else: raise ValueError("val must be a string!");

    def intValIsAtMaxOrAtMinX(self, val, x, usemax):
        if (usemax == True or usemax == False): pass;
        else: raise ValueError("usemax must be a boolean!");
        if (val == None or x == None): raise ValueError("x and val must be numbers!");
        if (type(val) == int and type(x) == int): pass;
        else: raise ValueError("x and val must be numbers!");
        if (self.disablevalidator): return True;
        #usemax means val <= x mean val must not be > x
        #usemin = true means x<=val means must not be val < x
        if (usemax): return (not(x < val));
        else: return (not(val < x));

    def intValIsAtMinimumX(self, val, x):
        return self.intValIsAtMaxOrAtMinX(val, x, False);

    def intValIsAtMaximumX(self, val, x):
        return self.intValIsAtMaxOrAtMinX(val, x, True);

    def intValIsAtMinXAndAtMaxY(self, val, x, y, varname = "varname"):
        #print(f"val = {val}");
        #print(f"x = {x}");
        #print(f"y = {y}");
        #print(f"varname = {varname}");
        vnmvld = self.strValHasAtMinXChars(varname, 1);
        if (vnmvld): pass;
        else: raise ValueError("varname must have at minimum 1 character on it!");
        if (y == None or x == None): raise ValueError("x and y must be numbers!");
        if (type(y) == int and type(x) == int): pass;
        else: raise ValueError("x and y must be numbers!");
        ageminvld = mv.intValIsAtMinimumX(val, x);
        if (ageminvld): pass;
        else: raise ValueError(f"{varname} must be at minimum {x}!");
        agemaxvld = mv.intValIsAtMaximumX(val, y);
        if (agemaxvld): pass;
        else: raise ValueError(f"{varname} must be at maximum {y}!");
        return val;

mv = MyValidator();

class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="activity", cascade="all, delete-orphan");
    
    # Add serialization rules
    #serialize_rules = ("-signups",);
    serialize_rules = ("-signups.activity",);
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    # Add relationship
    signups = db.relationship("Signup", back_populates="camper", cascade="all, delete-orphan");
    
    # Add serialization rules
    #serialize_rules = ("-signups",);
    serialize_rules = ("-signups.camper",);
    
    # Add validation
    @validates("name")
    def isvalidname(self, key, val):
        nmvld = mv.strValHasAtMinXChars(val, 1);
        if (nmvld): return val;
        else: raise ValueError("the camper must have a name!");

    @validates("age")
    def isvalidage(self, key, val):
        return mv.intValIsAtMinXAndAtMaxY(val, 8, 18, "age");
    
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)

    # Add relationships
    camper_id = db.Column(db.Integer, db.ForeignKey("campers.id"));
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"));
    camper = db.relationship("Camper", back_populates="signups");
    activity = db.relationship("Activity", back_populates="signups");
    
    # Add serialization rules
    #serialize_rules = ("-camper", "-activity");
    serialize_rules = ("-campers.signups", "-activity.signups");
    
    # Add validation
    @validates("time")
    def isvalidtime(self, key, val):
        return mv.intValIsAtMinXAndAtMaxY(val, 0, 23, "time");
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.

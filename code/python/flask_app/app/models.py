from flask_sqlalchemy import SQLAlchemy

# Define the DB object
db = SQLAlchemy()

# User Table
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    creation_date = db.Column(db.String(255), nullable=False)

    # Relationships
    personas_relation = db.relationship(
        'Persona', back_populates='user_relation', lazy=True)
    conversations_relation = db.relationship(
        'Conversation', back_populates='user_relation', lazy=True)
    messages_relation = db.relationship(
        'Message', back_populates='user_relation', lazy=True)

# Persona Table
class Persona(db.Model):
    __tablename__ = 'personas'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(), unique=False, nullable=False)
    dob = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(), nullable=False)
    profile_picture_filename = db.Column(db.String(), nullable=False)
    creation_date = db.Column(db.String(255), nullable=False)

    # Relationships
    user_relation = db.relationship(
        'User', back_populates='personas_relation', lazy=True)
    attributes_relation = db.relationship(
        'Attribute', back_populates='persona_relation', lazy=True)
    messages_relation = db.relationship(
        'Message', back_populates='persona_relation', lazy=True)
    conversation_participants_relation = db.relationship(
        'ConversationParticipants', back_populates='persona_relation', lazy=True)

# Attribute table
class Attribute(db.Model):
    __tablename__ = 'attributes'
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(db.Integer, db.ForeignKey(
        'personas.id'), nullable=False)
    attribute_type_id = db.Column(db.Integer, db.ForeignKey(
        'attribute_types.id'), nullable=False)
    value = db.Column(db.Float, nullable=False)

    # Relationships
    persona_relation = db.relationship(
        'Persona', back_populates='attributes_relation', lazy=True)
    attribute_type_relation = db.relationship(
        'AttributeType', back_populates='attributes_relation', lazy=True)

# AttributeType table
class AttributeType(db.Model):
    __tablename__ = 'attribute_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    left_name = db.Column(db.String(255), nullable=False)
    right_name = db.Column(db.String(255), nullable=False)

    # Relationships
    archetypes_relation = db.relationship(
        'Archetype', back_populates='attribute_type_relation', lazy=True)
    attributes_relation = db.relationship(
        'Attribute', back_populates='attribute_type_relation', lazy=True)

# Archetype table
class Archetype(db.Model):
    __tablename__ = 'archetypes'
    id = db.Column(db.Integer, primary_key=True)
    attribute_type_id = db.Column(db.Integer, db.ForeignKey(
        'attribute_types.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Float, nullable=False)

    # Relationships
    attribute_type_relation = db.relationship(
        'AttributeType', back_populates='archetypes_relation', lazy=True)

# Conversation table
class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic = db.Column(db.String(255), unique=False, nullable=False)
    created = db.Column(db.String(255), nullable=False)

    # Relationships
    user_relation = db.relationship(
        'User', back_populates='conversations_relation', lazy=True)
    
    messages_relation = db.relationship(
        'Message', back_populates='conversation_relation', lazy=True)
    
    conversation_participants_relation = db.relationship(
        'ConversationParticipants', back_populates='conversation_relation', lazy=True)

# Message table
class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(), nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    toxicity = db.Column(db.Float, nullable=False)
    content = db.Column(db.String(255), nullable=False)
    created = db.Column(db.String(255), nullable=False)

    # Relationships
    persona_relation = db.relationship(
        'Persona', back_populates='messages_relation', lazy=True)
    user_relation = db.relationship(
        'User', back_populates='messages_relation', lazy=True)
    conversation_relation = db.relationship(
        'Conversation', back_populates='messages_relation', lazy=True)

# ConversationParticipants table
class ConversationParticipants(db.Model):
    __tablename__ = 'conversation_participants'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    persona_id = db.Column(db.Integer, db.ForeignKey('personas.id'), nullable=False)
    role = db.Column(db.String(255), nullable=False)

    # Relationships
    conversation_relation = db.relationship(
        'Conversation', back_populates='conversation_participants_relation', lazy=True)
    persona_relation = db.relationship(
        'Persona', back_populates='conversation_participants_relation', lazy=True)
    
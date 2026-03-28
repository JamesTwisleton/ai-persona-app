"""
Seed data for preview environments.

Creates a test user, sample personas, and a sample conversation so that
PR preview environments have content to display immediately.

Called from docker-entrypoint.sh when ENV=preview.
"""

from app.database import SessionLocal
from app.models.user import User
from app.models.persona import Persona
from app.models.conversation import Conversation, ConversationParticipant, ConversationMessage
from sqlalchemy import select

PERSONAS = [
    {
        "name": "Dr. Elena Vasquez",
        "age": 42,
        "gender": "Female",
        "description": "A sharp bioethicist who spent a decade at the WHO. She approaches every debate with rigorous logic but isn't afraid to challenge the status quo.",
        "attitude": "Neutral",
        "ocean_openness": 0.85,
        "ocean_conscientiousness": 0.78,
        "ocean_extraversion": 0.55,
        "ocean_agreeableness": 0.45,
        "ocean_neuroticism": 0.30,
        "archetype_affinities": {"AN": 0.82, "PR": 0.71, "EX": 0.65, "IN": 0.58},
        "motto": "Evidence first, opinions second.",
        "unique_id": "prev01",
    },
    {
        "name": "Marcus Chen",
        "age": 28,
        "gender": "Male",
        "description": "A streetwear designer turned tech entrepreneur. Thinks in memes, speaks in hot takes, but has a surprisingly deep understanding of culture and markets.",
        "attitude": "Comical",
        "ocean_openness": 0.92,
        "ocean_conscientiousness": 0.35,
        "ocean_extraversion": 0.88,
        "ocean_agreeableness": 0.60,
        "ocean_neuroticism": 0.45,
        "archetype_affinities": {"EX": 0.90, "CR": 0.85, "RE": 0.55, "AN": 0.30},
        "motto": "If it's not weird, it's not worth doing.",
        "unique_id": "prev02",
    },
    {
        "name": "Grandma Phyllis",
        "age": 74,
        "gender": "Female",
        "description": "A retired schoolteacher from rural Yorkshire. She's seen empires rise and fall and has zero patience for nonsense. Surprisingly progressive but deeply pragmatic.",
        "attitude": "Sarcastic",
        "ocean_openness": 0.50,
        "ocean_conscientiousness": 0.82,
        "ocean_extraversion": 0.65,
        "ocean_agreeableness": 0.55,
        "ocean_neuroticism": 0.25,
        "archetype_affinities": {"PR": 0.80, "SE": 0.75, "AN": 0.50, "EX": 0.45},
        "motto": "Common sense isn't common anymore, love.",
        "unique_id": "prev03",
    },
    {
        "name": "Kai Okafor",
        "age": 35,
        "gender": "Non-binary",
        "description": "An environmental lawyer and part-time DJ from Lagos. Passionate about climate justice, effortlessly cool, and always ready with a counterargument.",
        "attitude": "Neutral",
        "ocean_openness": 0.80,
        "ocean_conscientiousness": 0.70,
        "ocean_extraversion": 0.75,
        "ocean_agreeableness": 0.50,
        "ocean_neuroticism": 0.40,
        "archetype_affinities": {"AN": 0.78, "EX": 0.72, "CR": 0.68, "PR": 0.60},
        "motto": "The planet doesn't negotiate.",
        "unique_id": "prev04",
    },
]

CONVERSATION_TOPIC = "Should AI be allowed to make hiring decisions for companies?"

MESSAGES = [
    {
        "persona_idx": 0,
        "text": "Let's be precise about what we're discussing. There's a spectrum — from AI screening CVs to AI making final hiring calls. The ethical calculus is very different at each point. I'd argue AI-assisted screening is defensible; autonomous hiring decisions are not, given current bias research.",
        "turn": 1,
    },
    {
        "persona_idx": 1,
        "text": "Hard disagree on the framing, doc. The current system is ALREADY biased — like, absurdly so. Your name, your uni, your photo — humans are pattern-matching machines running on vibes. At least an AI can be audited. You can't audit Dave from HR's gut feeling.",
        "turn": 1,
    },
    {
        "persona_idx": 2,
        "text": "Oh, bless. I taught for forty years and I can tell you — no machine would have spotted that the quiet lad in the back row was going to become a brilliant engineer. Hiring is about seeing people, not processing them. And if your Dave from HR is useless, replace Dave, don't replace humanity.",
        "turn": 1,
    },
    {
        "persona_idx": 3,
        "text": "Phyllis makes a fair point about intuition, but let's not romanticise it. In my work, I've seen how 'gut feeling' systematically disadvantages people from certain backgrounds. The question isn't AI vs. humans — it's which system produces more equitable outcomes, and how do we hold either accountable.",
        "turn": 1,
    },
    {
        "persona_idx": 0,
        "text": "Kai raises the accountability question, which is key. Under GDPR's Article 22, individuals have the right not to be subject to fully automated decisions. But the enforcement is patchy. We need regulatory frameworks that match the pace of deployment — and right now, they don't.",
        "turn": 2,
    },
    {
        "persona_idx": 1,
        "text": "Regulation is cool and all but it moves at government speed, which is basically continental drift. Meanwhile companies are already doing this. Maybe the move is transparency — if you're using AI in hiring, you have to publish your model's bias metrics. Open source the decision engine. Let the internet audit it.",
        "turn": 2,
    },
]


def seed():
    db = SessionLocal()
    try:
        # Check if already seeded
        existing = db.execute(
            select(User).where(User.email == "test@preview.local")
        ).scalar_one_or_none()

        if existing and len(existing.personas) > 0:
            print("Preview data already seeded, skipping.")
            return

        # Create or fetch test user
        if not existing:
            user = User(
                email="test@preview.local",
                google_id="preview-test-user",
                name="Preview Tester",
                is_admin=True,
                is_superuser=True,
            )
            db.add(user)
            db.flush()
        else:
            user = existing

        # Create personas
        persona_objects = []
        for p in PERSONAS:
            persona = Persona(user_id=user.id, is_public=True, **p)
            db.add(persona)
            persona_objects.append(persona)
        db.flush()

        # Create conversation
        convo = Conversation(
            topic=CONVERSATION_TOPIC,
            created_by=user.id,
            turn_count=2,
            max_turns=20,
            is_public=True,
            unique_id="prvcnv",
        )
        db.add(convo)
        db.flush()

        # Add participants
        for persona in persona_objects:
            db.add(ConversationParticipant(
                conversation_id=convo.id,
                persona_id=persona.id,
            ))

        # Add messages
        for msg in MESSAGES:
            persona = persona_objects[msg["persona_idx"]]
            db.add(ConversationMessage(
                conversation_id=convo.id,
                persona_id=persona.id,
                persona_name=persona.name,
                message_text=msg["text"],
                turn_number=msg["turn"],
                moderation_status="approved",
            ))

        db.commit()
        print(f"Seeded preview data: {len(persona_objects)} personas, 1 conversation, {len(MESSAGES)} messages.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding preview data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()

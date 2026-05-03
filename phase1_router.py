from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from config import embeddings
import numpy as np

# Personas

BOT_PERSONAS = {
    "bot_a": """
    I believe AI and crypto will solve all human problems.
    I am highly optimistic about technology, Elon Musk,
    and space exploration. I dismiss regulatory concerns.
    """,

    "bot_b": """
    I believe late-stage capitalism and tech monopolies
    are destroying society. I am highly critical of AI,
    social media, and billionaires. I value privacy and nature.
    """,

    "bot_c": """
    I strictly care about markets, interest rates,
    trading algorithms, and making money.
    I speak in finance jargon and view everything
    through the lens of ROI.
    """
}


# Convert Personas into Documents

persona_docs = [
    Document(
        page_content=persona,
        metadata={"bot_id": bot_id}
    )
    for bot_id, persona in BOT_PERSONAS.items()
]

# Create Vector Store
vectorstore = FAISS.from_documents(persona_docs, embeddings)

# Cosine Similarity Helper

def cosine_similarity(vec1, vec2):

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    return np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )

# Routing Function

def route_post_to_bots(post_content: str, threshold: float = 0.85):

    """
    Route user posts to relevant bots
    using vector similarity.
    """

    matched_bots = []

    # Post Embedding
    post_embedding = embeddings.embed_query(post_content)

    for bot_id, persona in BOT_PERSONAS.items():

        persona_embedding = embeddings.embed_query(persona)

        similarity = cosine_similarity(
            post_embedding,
            persona_embedding
        )

           if similarity >= threshold:

            matched_bots.append({
                "bot_id": bot_id,
                "similarity": round(float(similarity), 2)
            })

    return matched_bots

# Test Example

if __name__ == "__main__":

    post = "OpenAI just released a new AI model that may replace junior developers"

    results = route_post_to_bots(post)

    print("
PHASE 1 ROUTING")
    print("Matched Bots:")
    print(results)
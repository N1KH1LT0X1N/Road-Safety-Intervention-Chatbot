"""Setup script to process CSV and generate databases."""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.app.config import settings
from backend.app.utils.data_processor import DataProcessor
from backend.app.services.gemini_service import GeminiService
from backend.app.services.vector_store import VectorStoreService
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def main():
    """Main setup function."""
    logger.info("=" * 60)
    logger.info("ROAD SAFETY INTERVENTION DATABASE SETUP")
    logger.info("=" * 60)

    try:
        # Step 1: Process CSV data
        logger.info("\n[1/4] Processing CSV data...")

        csv_path = Path("GPT_Input_DB(Sheet1).csv")
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            logger.error("Please ensure GPT_Input_DB(Sheet1).csv is in the project root")
            return

        processor = DataProcessor(csv_path)
        df = processor.process()

        logger.info(f"Processed {len(df)} interventions")

        # Step 2: Save processed data
        logger.info("\n[2/4] Saving processed data...")

        output_dir = settings.processed_data_dir
        saved_files = processor.save_processed_data(output_dir)

        for file_type, file_path in saved_files.items():
            logger.info(f"Saved {file_type}: {file_path}")

        # Step 3: Generate embeddings
        logger.info("\n[3/4] Generating embeddings with Gemini...")

        gemini_service = GeminiService()

        # Prepare documents
        documents = []
        metadatas = []
        ids = []

        for idx, row in df.iterrows():
            # Create document text
            doc_text = row.get("search_text", "")
            if not doc_text:
                doc_text = f"{row['problem']} {row['category']} {row['type']} {row['data']}"

            documents.append(doc_text)

            # Create metadata (ChromaDB only supports simple types)
            metadata = {
                "id": row["id"],
                "s_no": int(row["S. No."]) if "S. No." in row else int(row["s_no"]) if "s_no" in row else 0,
                "problem": str(row["problem"]),
                "category": str(row["category"]),
                "type": str(row["type"]),
                "code": str(row["code"]),
                "clause": str(row["clause"]),
                "data": str(row["data"])[:500],  # Truncate for metadata
            }

            # Add optional fields if available
            if "speed_min" in row and row["speed_min"] is not None:
                metadata["speed_min"] = int(row["speed_min"])
            if "speed_max" in row and row["speed_max"] is not None:
                metadata["speed_max"] = int(row["speed_max"])
            if "priority" in row and row["priority"]:
                metadata["priority"] = str(row["priority"])

            metadatas.append(metadata)
            ids.append(row["id"])

        logger.info(f"Prepared {len(documents)} documents for embedding")

        # Generate embeddings in batches
        logger.info("Generating embeddings (this may take a few minutes)...")
        embeddings = await gemini_service.generate_embeddings(documents)

        logger.info(f"Generated {len(embeddings)} embeddings")

        # Step 4: Create vector store
        logger.info("\n[4/4] Creating vector store...")

        vector_store = VectorStoreService(
            persist_directory=str(settings.chroma_dir), collection_name=settings.collection_name
        )

        # Create collection
        vector_store.create_collection()

        # Add documents
        vector_store.add_documents(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)

        logger.info(f"Vector store created with {vector_store.count()} documents")

        # Success
        logger.info("\n" + "=" * 60)
        logger.info("✅ DATABASE SETUP COMPLETE!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Create a .env file based on .env.example")
        logger.info("2. Add your Gemini API key to .env")
        logger.info("3. Generate API keys for authentication")
        logger.info("4. Start the backend: uvicorn backend.app.main:app --reload")
        logger.info("5. Visit http://localhost:8000/docs for API documentation")

    except Exception as e:
        logger.error(f"\n❌ Setup failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

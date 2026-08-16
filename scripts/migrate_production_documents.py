import os
import sys

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath("."))

from backend.app.core.database import SessionLocal
from backend.app.models.document import Document
from backend.app.services.storage import upload_file_to_storage, get_storage_key
from backend.app.services.startup import _reindex_document_from_bytes
from backend.app.services.vector_store import get_collection

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/migrate_production_documents.py <source-directory> [--dry-run]")
        sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--dry-run"]

    if not args:
        print("Usage: python scripts/migrate_production_documents.py <source-directory> [--dry-run]")
        sys.exit(1)

    source_dir = args[0]
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        sys.exit(1)

    if dry_run:
        print("==================================================")
        print("MIGRATION DRY RUN MODE — NO CHANGES WILL BE MADE")
        print("==================================================")

    db = SessionLocal()
    try:
        active_docs = db.query(Document).filter(Document.is_active == True).all()
        print(f"Found {len(active_docs)} active document records in PostgreSQL DB.")

        matched_files = {}
        for root, _, files in os.walk(source_dir):
            for f in files:
                full_path = os.path.join(root, f)
                matched_files[f.lower()] = full_path

        coll = get_collection()

        migrated_count = 0
        for doc in active_docs:
            fname_lower = doc.filename.lower()
            obj_key = get_storage_key(doc.document_id, doc.filename)
            res = coll.get(where={"document_id": doc.document_id})
            vector_count = len(res.get("ids", []))

            if fname_lower in matched_files:
                src_path = matched_files[fname_lower]
                if dry_run:
                    print(f"\n[DRY RUN] Document ID: {doc.document_id}")
                    print(f"          Filename: {doc.filename}")
                    print(f"          Matched Source File: {src_path}")
                    print(f"          R2 Storage Object Key: {obj_key}")
                    print(f"          Current ChromaDB Vector Count: {vector_count}")
                    print(f"          Planned Action: Upload raw source file to R2 & verify vectors")
                else:
                    print(f"\n--- Ingesting document: '{doc.filename}' (ID: {doc.document_id[:8]}) ---")
                    with open(src_path, "rb") as f:
                        content = f.read()

                    upload_ok = upload_file_to_storage(content, obj_key)
                    if upload_ok:
                        print(f"✅ Uploaded source file to storage key: '{obj_key}'")

                    if vector_count == 0:
                        print("ChromaDB vectors missing. Ingesting & re-indexing into ChromaDB...")
                        new_chunks = _reindex_document_from_bytes(doc, content)
                        if new_chunks > 0:
                            doc.status = "processed"
                            doc.chunk_count = new_chunks
                            migrated_count += 1
                            print(f"✅ Re-indexed {new_chunks} vectors into ChromaDB!")
                        else:
                            print("⚠️ Re-indexing returned 0 chunks.")
                    else:
                        print("✅ ChromaDB vectors already verified. No re-indexing needed.")
            else:
                print(f"\n[WARNING] Source file for '{doc.filename}' (ID: {doc.document_id[:8]}) NOT FOUND in '{source_dir}'.")

        if not dry_run:
            db.commit()
            print(f"\nMigration completed successfully. Migrated/indexed {migrated_count} documents.")
        else:
            print("\nDry run completed. Zero changes made.")
    except Exception as err:
        db.rollback()
        print(f"\nError during migration: {err}")
    finally:
        db.close()

if __name__ == "__main__":
    main()

from backend.app.rag import (
    InMemoryVectorStore,
    RagChunk,
    RagDocument,
    RagSearchResult,
    RagSource,
    RetrievalService,
    SimpleChunker,
    SimpleDocumentLoader,
)


def test_rag_module_importable() -> None:
    assert RagDocument is not None
    assert RagChunk is not None
    assert RagSource is not None
    assert RagSearchResult is not None
    assert SimpleDocumentLoader is not None
    assert SimpleChunker is not None
    assert InMemoryVectorStore is not None
    assert RetrievalService is not None


def test_simple_document_loader_loads_entries() -> None:
    entries = [
        {
            "id": "doc-1",
            "title": "Test Document",
            "text": "Bu bir test belgesidir.",
            "source": {
                "title": "Example Source",
                "url": "https://example.com",
                "type": "faq",
            },
        }
    ]
    loader = SimpleDocumentLoader(entries)
    documents = loader.load()

    assert len(documents) == 1
    assert documents[0].id == "doc-1"
    assert documents[0].title == "Test Document"
    assert documents[0].text == "Bu bir test belgesidir."
    assert documents[0].source.title == "Example Source"


def test_simple_chunker_creates_chunks_with_overlap() -> None:
    document = RagDocument(
        id="doc-1",
        title="Chunk Test",
        text="""Bu belge, küçük bir test metni içerir ve parçalanabilir.
            İçerik birkaç cümleye ayrılacaktır.""",
    )
    chunker = SimpleChunker(chunk_size=40, overlap=10)
    chunks = chunker.chunk(document)

    assert len(chunks) >= 2
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].start == 0
    assert chunks[0].end <= 40
    assert chunks[1].start < chunks[0].end


def test_in_memory_vector_store_search_returns_relevant_chunks() -> None:
    chunk_one = RagChunk(
        id="doc-1-0",
        document_id="doc-1",
        text="Bölüm telefon numarası: +90 462 ...",
        start=0,
        end=28,
    )
    chunk_two = RagChunk(
        id="doc-2-0",
        document_id="doc-2",
        text="Staj süresi toplam 60 gündür.",
        start=0,
        end=26,
    )
    store = InMemoryVectorStore()
    store.add_chunks([chunk_one, chunk_two])
    results = store.search("telefon", top_k=2)

    assert len(results) == 1
    assert results[0].id == "doc-1-0"


def test_retrieval_service_returns_search_result_structure() -> None:
    document = RagDocument(
        id="doc-1",
        title="İletişim Bilgisi",
        text="Bölüm telefon numarası: +90 462 377 31 57",
        source=RagSource(
            title="İletişim sayfası",
            url="https://example.edu/iletisim",
            source_type="faq",
        ),
    )
    loader = SimpleDocumentLoader([
        {
            "id": document.id,
            "title": document.title,
            "text": document.text,
            "source": {
                "title": document.source.title,
                "url": document.source.url,
                "type": document.source.source_type,
            },
        }
    ])
    documents = loader.load()

    store = InMemoryVectorStore()
    service = RetrievalService(vector_store=store)
    service.index_documents(documents)

    result = service.retrieve("telefon", top_k=1)

    assert isinstance(result, RagSearchResult)
    assert result.query == "telefon"
    assert result.chunks
    assert result.sources
    assert result.sources[0].title == "İletişim sayfası"

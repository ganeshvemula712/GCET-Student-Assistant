import api from "./api";

const documentService = {
  // Get all uploaded documents with optional category filter
  async getDocuments(category = null) {
    const params = category && category !== "All" ? { category } : {};
    const response = await api.get("/documents", { params });
    return response.data;
  },

  // Upload a document with optional versioning supersedesId, category, and tags
  async uploadDocument(file, supersedesId = null, category = "General Academic", tags = "") {
    const formData = new FormData();
    formData.append("file", file);
    if (supersedesId) {
      formData.append("supersedes_id", supersedesId);
    }
    if (category) {
      formData.append("category", category);
    }
    if (tags) {
      formData.append("tags", tags);
    }

    const response = await api.post(
      "/documents/upload",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  },

  // Delete a document
  async deleteDocument(documentId) {
    const response = await api.delete(
      `/documents/${documentId}`
    );

    return response.data;
  },

  // Re-index a document from cloud storage
  async reindexDocument(documentId) {
    const response = await api.post(`/documents/${documentId}/reindex`);
    return response.data;
  },
};

export default documentService;
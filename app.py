import warnings
import os
#import sys
import io
import gradio as gr
from contextlib import redirect_stderr

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from transformers import pipeline
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFacePipeline
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAGSystem:
    def __init__(self):
        self.llm = None
        self.retriever = None
        self.vectorStore = None

        self.setup_model()

    def setup_model(self):
        """Initialize the language model"""

        pipe = pipeline(
            "text2text-generation",
            model="google/flan-t5-large",
            max_new_tokens=600,
            min_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

        self.llm = HuggingFacePipeline(pipeline=pipe)

    def process_pdf(self, pdf_file):
        """Process uploaded PDF and create vector store"""

        try:
            if pdf_file is None:
                return "Please upload a PDF file first!"
            
            tempPath = "data/temp_upload.pdf"

            with open(tempPath, "wb") as f:
                f.write(pdf_file)

            loader = PyPDFLoader(tempPath)
            doc = loader.load()

            textSplitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                add_start_index=True,
            )

            splits = textSplitter.split_documents(doc)

            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

            f = io.StringIO()

            with redirect_stderr(f):

                self.vectorStore = Chroma(
                    collection_name="uploaded_document",
                    embedding_function=embeddings,
                    persist_directory="./dbStore",
                )

                self.vectorStore.add_documents(splits)

            self.retriever = self.vectorStore.as_retriever(search_kwargs={"k": 5})

            os.remove(tempPath)

            return f"✅ PDF processed successfully! \n📄 Document loaded with {len(doc)} pages \n📝 Split into {len(splits)} chunks \n🔍 Ready for questions!"
        
        except Exception as e:
            return f"❌ Error processing PDF: {str(e)}"
        
    def retrieve_docs(self, query):
        """Retrieve relevant documents"""

        if self.retriever is None:
            return []
        
        f = io.StringIO()

        with redirect_stderr(f):
            return self.retriever.invoke(query)
        

    def generate_answer(self, query, docs):
        """Generate answer using retrieved documents"""

        if not docs:
            return "No relevant documents found. Please make sure you've uploaded and processed a PDF."
        
        docsContent = "\n\n".join(doc.page_content for doc in docs)
        
        prompt = f"""
            You are an assistant that answers questions using the provided context. 

            Rules:
            - DO NOT copy text directly.
            - Summarize and explain in clear English.
            - Answer in 4–6 complete sentences.
            If the context is limited, give the best possible summary instead of refusing.

            Context:
            {docsContent}

            Question:
            {query}

            Answer:

            """

        try:
            response = self.llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error generating response: {str(e)}"
        
    def answer_question(self, question):
        """Main function to answer questions"""

        if not question.strip():
            return "Please enter a question!!", ""
        
        if self.retriever is None:
            return "Please upload and process a PDF document first!", ""
        
        docs = self.retrieve_docs(question)

        if not docs:
             return "No relevant information found for your question.", ""
        
        answer = self.generate_answer(question, docs)

        contextDisplay = "\n\n".join([f"📄 Chunk {i+1}:\n{doc.page_content[:300]}..." 
                                     for i, doc in enumerate(docs[:3])])
        
        return answer, contextDisplay

ragSystem = RAGSystem()
# Create Gradio Interface
def create_interface():
    with gr.Blocks(title="Project-Orpheus", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📚 VectorDoc Assistant: RAG Document Q&A System")
        gr.Markdown("Upload a PDF document and ask questions about its content!")

        with gr.Row():
            with gr.Column(scale=1):
                # PDF Upload Section
                gr.Markdown("## 📄 Upload Document")
                pdfUpload = gr.File(
                    label="Upload PDF",
                    file_types=[".pdf"],
                    type="binary"
                )

                processBtn = gr.Button("🔄 Process PDF", variant="primary")
                statusOutput = gr.Textbox(
                    label="Status",
                    lines=4,
                    interactive=False
                )

            with gr.Column(scale=2):
                # Q&A Section
                gr.Markdown("## 💭 Ask Questions")
                questionInput = gr.Textbox(
                    label="Your Question",
                    placeholder="What is the main topic of this document?",
                    lines=2
                )
                askBtn = gr.Button("🤔 Ask Question", variant="primary")
                
                answerOutput = gr.Textbox(
                    label="Answer",
                    lines=8,
                    interactive=False
                )
                
                with gr.Accordion("📋 Retrieved Context", open=False):
                    context_output = gr.Textbox(
                        label="Relevant Document Chunks",
                        lines=10,
                        interactive=False
                    )

        # Example questions
        gr.Markdown("## 🎯 Example Questions")
        exampleQuestions = [
            "What is the main topic of this document?",
            "What are the key findings or conclusions?",
            "What methodology was used?",
            "What are the main challenges discussed?"
        ]
        
        with gr.Row():
            for question in exampleQuestions:
                gr.Button(question, size="sm").click(
                    fn=lambda q=question: q,
                    outputs=questionInput
                )
    
        # Event handlers
        processBtn.click(
            fn=ragSystem.process_pdf,
            inputs=pdfUpload,
            outputs=statusOutput
        )
        
        askBtn.click(
            fn=ragSystem.answer_question,
            inputs=questionInput,
            outputs=[answerOutput, context_output]
        )
        
        # Allow Enter key to submit question
        questionInput.submit(
            fn=ragSystem.answer_question,
            inputs=questionInput,
            outputs=[answerOutput, context_output]
        )
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("💡 **Note**: Upload a PDF first, then ask specific questions about its content!")
    
    return demo


if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True
    )
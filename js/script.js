document.addEventListener("DOMContentLoaded", () => {
    const uploadInput = document.getElementById("pdf-upload");
    const generateBtn = document.getElementById("generate-btn");
    const flashcardsContainer = document.getElementById("flashcards-container");
  
    generateBtn.addEventListener("click", async () => {
      const file = uploadInput.files[0];
  
      if (!file) {
        alert("Please upload a PDF file first.");
        return;
      }
  
      const formData = new FormData();
      formData.append("pdf", file);
  
      flashcardsContainer.innerHTML = "<p class='placeholder-text'>Generating flashcards, please wait...</p>";
  
      try {
        const response = await fetch("https://flashcard-3ppu.onrender.com/upload-pdf", {
            method: "POST",
            body: formData
          });    
  
        const data = await response.json();
  
        flashcardsContainer.innerHTML = "";
  
        data.flashcards.forEach(card => {
          const cardEl = document.createElement("div");
          cardEl.className = "flashcard";
  
          cardEl.innerHTML = `
            <div class="flashcard-question">Q: ${card.question}</div>
            <div class="flashcard-answer">A: ${card.answer}</div>
          `;
  
          flashcardsContainer.appendChild(cardEl);
        });
  
      } catch (err) {
        console.error("Error generating flashcards:", err);
        flashcardsContainer.innerHTML = "<p class='placeholder-text'>Failed to generate flashcards. Try again.</p>";
      }
    });
  });
  

// Display Current Date
document.getElementById("dateday").textContent = new Date().toLocaleDateString(
  "en-IN",
  {
    day: "numeric",
    month: "short",
    year: "numeric",
  },
);

// Count Elements
const pendingcount = document.querySelector(".pending-count");
const completecount = document.querySelector(".completed-count");

// Loop Through All Tasks
document.querySelectorAll(".task").forEach((task) => {
  const taskName = task.querySelector(".task-name");
  const editInput = task.querySelector(".edit-input");
  const editBtn = task.querySelector(".edit-task");
  const saveBtn = task.querySelector(".save-task");
  const cancelBtn = task.querySelector(".cancel-task");
  const calender = task.querySelector(".calender-color");
  const deleteBtn = task.querySelector(".delete-task");
  const checkbox = task.querySelector(".task-checkbox");
  

  // EDIT TASK
  editBtn.addEventListener("click", () => {
    taskName.style.display = "none";
    editInput.style.display = "block";

    editBtn.style.display = "none";
    saveBtn.style.display = "inline-block";
    cancelBtn.style.display = "inline-block";

    calender.style.display = "none";
    deleteBtn.style.display = "none";

    editInput.focus();
  });

  // CANCEL EDIT
  cancelBtn.addEventListener("click", () => {
    editInput.value = taskName.textContent.trim();

    taskName.style.display = "block";
    editInput.style.display = "none";

    editBtn.style.display = "inline-block";
    saveBtn.style.display = "none";
    cancelBtn.style.display = "none";

    calender.style.display = "flex";
    deleteBtn.style.display = "inline-block";
  });

  // SAVE UPDATED TASK
  saveBtn.addEventListener("click", async () => {
    const updatedText = editInput.value.trim();
    const taskId = task.dataset.id;

    if (updatedText === "") {
      alert("Task cannot be empty!!");
      return;
    }

    try {
      const response = await fetch(`/update-task/${taskId}`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          task: updatedText,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        alert(result.message);
        return;
      }

      taskName.textContent = updatedText;

      taskName.style.display = "block";
      editInput.style.display = "none";

      editBtn.style.display = "inline-block";
      saveBtn.style.display = "none";
      cancelBtn.style.display = "none";

      calender.style.display = "flex";
      deleteBtn.style.display = "inline-block";

      alert("Task Updated successfully!");
    } catch (error) {
      console.log("Error:", error);
      alert("Something went wrong!");
    }
  });

  // DELETE TASK
  deleteBtn.addEventListener("click", async () => {
    const taskId = task.dataset.id;
    const taskstatus = task.dataset.status;
    const confirmDelete = confirm("Are you sure you want to delete this task?");

    if (!confirmDelete) {
      return;
    }

    try {
      const response = await fetch(`/delete-task/${taskId}`, {
        method: "POST",
      });

      const result = await response.json();

      if (!response.ok) {
        alert(result.message);
        return;
      }

      task.remove();
      let pending1 = Number(pendingcount.textContent.match(/\d+/)[0]);

      let completed1 = Number(completecount.textContent.match(/\d+/)[0]);
      pending1 = pending1 - 1;
      completed1 = completed1 - 1;
      if (pending1 < 0){
        pending1 = 0;
      }
      if(completed1 < 0){
        completed1 = 0;
      }
      pendingcount.textContent = `Pending (${pending1})`;
      completecount.textContent = `Completed (${completed1})`;

      alert("Task deleted successfully!");
    } catch (error) {
      console.log("Error:", error);
      alert("Something went wrong!");
    }
  });

  // CHECKBOX - COMPLETE / PENDING
  checkbox.addEventListener("click", async () => {
    const taskId = task.dataset.id;

    // Get Current Status
    const currentStatus = Number(task.dataset.status);

    // Change Status
    const newStatus = currentStatus === 0 ? 1 : 0;

    try {
      const response = await fetch(`/toggle-task/${taskId}`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          status: newStatus,
        }),
      });

      const result = await response.json();

      console.log("Status Code:", response.status);
      console.log("Server Response:", result);

      if (!response.ok) {
        alert(result.message);
        return;
      }

      // COUNT UPDATE
      let pending = Number(pendingcount.textContent.match(/\d+/)[0]);

      let completed = Number(completecount.textContent.match(/\d+/)[0]);

      if (currentStatus === 0) {
        pending--;
        completed++;
      } else {
        pending++;
        completed--;
      }

      pendingcount.textContent = `Pending (${pending})`;
      completecount.textContent = `Completed (${completed})`;

      // Update Current Status
      task.dataset.status = newStatus;

      // Change Icon and Task Style
      if (newStatus === 1) {
        checkbox.className = "fa-solid fa-circle-check task-checkbox";

        taskName.style.textDecoration = "line-through";
      } else {
        checkbox.className = "fa-regular fa-circle task-checkbox";

        taskName.style.textDecoration = "none";
      }
    } catch (error) {
      console.log("Error:", error);
      alert("Error: " + error.message);
    }
  });
});

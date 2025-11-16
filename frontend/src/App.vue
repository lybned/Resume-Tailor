
<template>
  <div class="p-4 w-full">
    <h2>Job Description</h2>

    <textarea
      v-model="job"
      placeholder="Type something here..."
      rows="5"
      class="border p-2 w-full"
    ></textarea>

    <button
      @click="get_skill_list"
      class="mt-2 bg-blue-500 text-black px-4 py-2 rounded"
    > Extract Skill List</button>

    <h2>Resume</h2>
    <input type="file" @change="handleFileSelect" accept="application/pdf" />

    <button
      @click="sendBuffer"
      class="mt-2 bg-blue-500 text-black px-4 py-2 rounded"
    >
      Extract Text From Resume
    </button>
    <div class="flex justify-center">
      <div class="p-6 w-5/6 ">
        <div 
          v-for="(title, index) in title_list" 
          :key="title" 
          class="mb-6 border-b pb-4 flex"
        >    
          <div class="w-1/2">
            <button @click="change_edit(index)" >Edit</button>     
            <div v-if="edit_list[index]">
              <h2 class="text-xl font-bold mb-2 text-left">{{ title_list[index] }}</h2>
              <ul class="list-disc list-inside space-y-1 text-left">
                <li v-for="(item, index) in content_list[index].split('\n')" :key="index">
                  {{ item }}
                </li>
              </ul>
            </div> 
            
            <div v-else>
              <input class="w-full p-2 mb-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent"
              v-model="title_list_buff[index]" placeholder="Category name" /><br/>
              <textarea
                v-model="content_list_buff[index]"
                placeholder="Enter one item per line"
                rows=4
                class="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent resize-none"
              ></textarea>
              <button @click="edit_text(index)">Change</button>
            </div>

            
            <button
              @click="tailor_section(index)"
              class="mt-2 bg-blue-500 text-black px-4 py-2 rounded"
            >      Tailor Toward Job Description
            </button>            
          </div>
          <div class="w-1/2">
            <p v-if="ai_tailor[index]" class="mt-2 whitespace-pre-line">{{ ai_tailor[index] }}</p>
          </div>

        </div>
      </div>
      
    </div>

    <!-- 
    <h2>Ask Questions</h2>

    <textarea
      v-model="ask_chat"
      placeholder="Type something here..."
      rows="5"
      class="border p-2 w-full"
    ></textarea>

    <button
      @click="send_chat"
      class="mt-2 bg-blue-500 text-black px-4 py-2 rounded"
    >      Send Buffer to API 2
    </button>

      <div v-if="ai_response" class="mt-2 whitespace-pre-line">
        {{ ai_response }}
      </div>  --> 
  </div>
</template>

<script setup lang="ts">
  import { ref } from 'vue'

  const job = ref('')  // this is your on-screen buffer
  const responseMessage = ref('')

  const skillList = ref("")

  const selectedFile = ref(null); // Store the chosen file
  const progress = ref(0);        // Track upload progress

  const ask_chat = ref('')

  const ai_response = ref("")

  const organized_text = ref({})
  const organized_text_mod = ref({})


  const title_list_buff = ref([])
  const content_list_buff  = ref([])

  const title_list = ref([])
  const content_list  = ref([])

  const edit_list = ref([])
  const ai_tailor = ref([])

  const tailor_result = ref("")



  const handleFileSelect = (event) => {
    selectedFile.value = event.target.files[0] || null;
    progress.value = 0; // reset progress on new file selection
  };

  function edit_text(index){
    title_list.value[index] = title_list_buff.value[index]
    content_list.value[index] = content_list_buff.value[index]
  }

  function change_edit(index){
    edit_list.value[index] = !edit_list.value[index]
  }

  async function send_chat(){
    const payload = { session_id: session_id.value, question: ask_chat.value };

    try {
      const response = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST", // or "PUT"
        headers: {
          "Content-Type": "application/json", // tell backend it's JSON
        },
        body: JSON.stringify(payload), // convert JS object to JSON
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json(); // parse JSON response
      ai_response.value = data["result"]
      console.log("Response from backend:", data);
    } catch (error) {
      console.error("Error sending data:", error);
    }

  }

  async function tailor_section(index){
    if (job.value.length < 5){
      alert("Make sure job description is filled")
      return ""
    }
    const title = title_list.value[index]
    const texts = content_list.value[index]

    const payload = { title: title, texts: texts, job:job.value};

    try {
      const response = await fetch("http://127.0.0.1:5000/tailor", {
        method: "POST", // or "PUT"
        headers: {
          "Content-Type": "application/json", // tell backend it's JSON
        },
        body: JSON.stringify(payload), // convert JS object to JSON
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json(); // parse JSON response
      ai_tailor.value[index] = data["result"]
      

      console.log("Response from backend:", data);
    } catch (error) {
      console.error("Error sending data:", error);
    }    
  }


  async function get_skill_list(){
    const payload = { job:job.value};

    try {
      const response = await fetch("http://127.0.0.1:5000/extract_skills", {
        method: "POST", // or "PUT"
        headers: {
          "Content-Type": "application/json", // tell backend it's JSON
        },
        body: JSON.stringify(payload), // convert JS object to JSON
      });

      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const data = await response.json(); // parse JSON response
      skillList.value = data["result"]
      

      console.log("Response from backend:", data);
    } catch (error) {
      console.error("Error sending data:", error);
    }   
  }

  async function sendBuffer() {
    try{

    const formData = new FormData();
    formData.append("file", selectedFile.value);
    formData.append("job", job.value);     // extra text

    const response = await fetch("http://127.0.0.1:5000/process", {
      method: "POST",
      body: formData
    });
    
    //JSON.stringify({ job: job.value, experience: experience.value, education:education.value})

    const result = await response.json()
      responseMessage.value = 'Sent successfully!'
      responseMessage.value = result["resume_text"]
      organized_text.value = result["organized_text"]
      organized_text_mod .value = result["organized_text"]

      title_list.value = []
      content_list.value = []
      title_list_buff.value = []
      content_list_buff.value = []

      edit_list.value = Array(Object.values(result["organized_text"]).length).fill(true);
      ai_tailor.value = Array(Object.values(result["organized_text"]).length).fill("");
      // Populate reactive data
      for (const key in result["organized_text"]) {
        title_list.value.push(key)
        title_list_buff.value.push(key)
        content_list.value.push(result["organized_text"][key].join("\n"))
        content_list_buff.value.push(result["organized_text"][key].join("\n"))
      }
      console.log(result["organized_text"])
    } catch (err) {
      responseMessage.value = 'Error sending buffer'
      console.error(err)
    }

  }
</script>

<style scoped>
  
</style>

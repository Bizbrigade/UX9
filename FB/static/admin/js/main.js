
var formdata = new FormData();
var allFields = document.querySelectorAll('.FormDataInput');
var textARea=document.querySelectorAll('.FormDataInputrewwe');
// var textEditor = document.querySelector('.note-editor');
// textEditor.classList.add("FormDataInput");
// var formdata = new FormData();

// let vv = document.querySelector('#blog-content');
// console.log(vv.type)

function textAreaChanged(text_area_name, text_area_contents){
     console.log(text_area_contents);
     formdata.append(text_area_name, text_area_contents);
}
// $('#text-area-summernote').on('summernote.change', function( we, contents,$editable) {
//      console.log('summernote\'s content is changed.');
//      // formdata.append(this.name, contents);
//      console.log(this.name, contents);
//      // formdata.append( );
//      // console.log(we);
//      // console.log(contents);
//      // console.log($editable);

//    });

console.log(allFields + ' allFields');
allFields.forEach(element => {
     element.addEventListener('change', (e) => {
          console.log(e.target.name, e.target.value);
          if(e.target.type == 'file') {
               for (let x = 0; x < e.target.files.length; x++) {
                    formdata.append(e.target.name, e.target.files[x]);
               }
          } 
          // else if(e.target.type == 'textarea') {
          //      formdata.append(e.target.name, e.target.innerHTML);
          //      console.log('textarea ' + e.target.innerHTML);
          //      console.log('e.target.name ' + e.target.name);
          //      console.log('e.target.innerHTML ' + e.target.innerHTML);
          // } 
          else {
               formdata.append(e.target.name, e.target.value);
          }
     })
})

function send_data(url){
     let UpdatedForm = document.getElementById('updateSubmitBtn'); 
     UpdatedForm.addEventListener('click', function (event) { 
     event.preventDefault()
     axios.post(url, formdata,
          {headers: {
               'accept': 'application/json',
               'Content-Type': `multipart/form-data;`,
               'X-CSRFToken': document.getElementById('csrf-token').querySelector('input').value}
          })
          .then(
               function (response) {
                    if (response.data.status == true ){
                         alert(response.data.msg);
                    }
                    else{
                         alert(response.data.msg);
                    }
               location.reload();
          })
          .catch(errors => console.log(errors))
     })
}


// ======= Dark Mode JS =========

let darkBtn = document.getElementById('dark-button');
darkBtn.addEventListener('click', function () {
     document.getElementById('body').classList.toggle('dark-mode');
});

// ===== Calculator Logic ===
var price = document.getElementById("price");
var flatValue = document.getElementById("flatValue");
var numPercentage = document.getElementById("numPercentage");



function calculate_number() {
     var first_number = parseFloat(price.value);
     if (isNaN(first_number)) first_number = 0;

     var second_number = parseFloat(flatValue.value);
     if (isNaN(second_number)) second_number = 0;

     var third_number = parseFloat(numPercentage.value);
     if (isNaN(third_number)) third_number = 0;

     //  Calculation if else condition
     if (flatValue.disabled === false) {
          var result = first_number - second_number;
     } else {
          var result = first_number - ((first_number * third_number) / 100);
     }

     //  Print Value
     document.getElementById("sprice").value = result;
}

// ===== Show hide function == 
function showContent(checkboxPara) {
     document.getElementById(checkboxPara).style.display = 'block';
}
function hideContent(checkboxPara) {
     document.getElementById(checkboxPara).style.display = 'none';
}





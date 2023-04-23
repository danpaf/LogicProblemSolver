window.onload = function() {
  const inputField = document.getElementById('inputField');
  const datalist = document.getElementById('options');

  inputField.addEventListener('input', function() {
    let inputVal = this.value;
    let optionsArr = Array.from(datalist.options);

    let filteredOptions = optionsArr.filter(function(option) {
      return option.value.toLowerCase().startsWith(inputVal.toLowerCase());
    });

    datalist.innerHTML = '';

    filteredOptions.forEach(function(option) {
      datalist.appendChild(option);
    });
  });
};
window.onload = function() {
  const inputField1 = document.getElementById('inputField1');
  const datalist1 = document.getElementById('options1');

  inputField1.addEventListener('input', function() {
    let inputVal = this.value;
    let optionsArr = Array.from(datalist1.options);

    let filteredOptions = optionsArr.filter(function(option) {
      return option.value.toLowerCase().startsWith(inputVal.toLowerCase());
    });

    datalist1.innerHTML = '';

    filteredOptions.forEach(function(option) {
      datalist1.appendChild(option);
    });
  });
};


// window.onload = function() {
//   const inputField2 = document.getElementById('inputField2');
//   const datalist2 = document.getElementById('options2');
//
//   inputField2.addEventListener('input', function() {
//     let inputVal = this.value;
//     let optionsArr = Array.from(datalist2.options);
//
//     let filteredOptions = optionsArr.filter(function(option) {
//       return option.value.toLowerCase().startsWith(inputVal.toLowerCase());
//     });
//
//     datalist2.innerHTML = '';
//
//     filteredOptions.forEach(function(option) {
//       datalist2.appendChild(option);
//     });
//   });
// };





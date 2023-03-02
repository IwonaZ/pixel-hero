$('#submitErrorMessage').hide();
$('#submitSuccessMessage').hide();

function validateName() {

    var name = document.getElementById('name').value;

    if(name.length == 0) {

      producePrompt('Name is required', 'name-error' , 'red')
      return false;

  }

  if (!name.match(/^[A-Za-z]*\s{1}[A-Za-z]*$/)) {

      producePrompt('First and last name, please.','name-error', 'red');
      return false;

  }

  producePrompt('Valid', 'name-error', 'green');
  setTimeout(function(){jsHide('name-error');}, 1000);
  return true;

}

function validatePhone() {

var phone = document.getElementById('phone').value;

if(phone.length == 0) {
    //producePrompt('Phone number is required.', 'phone-error', 'red');
    return true;
}

if(phone.length != 10) {
    producePrompt('Include area code.', 'phone-error', 'red');
    return false;
}

if(!phone.match(/^[0-9]{10}$/)) {
    producePrompt('Only digits, please.' ,'phone-error', 'red');
    return false;
}

producePrompt('Valid', 'phone-error', 'green');
setTimeout(function(){jsHide('phone-error');}, 1000);
return true;

}

function validateEmail () {

var email = document.getElementById('email').value;

if(email.length == 0) {

  producePrompt('Email Invalid','email-error', 'red');
  return false;

}

if(!email.match(/^[A-Za-z\._\-[0-9]*[@][A-Za-z]*[\.][a-z]{2,4}$/)) {

  producePrompt('Email Invalid', 'email-error', 'red');
  return false;

}

producePrompt('Valid', 'email-error', 'green');
    setTimeout(function(){jsHide('email-error');}, 1000);
    return true;
}

function validateMessage() {
var message = document.getElementById('message').value;
var required = 10;
var left = required - message.length;

if (left > 0) {
  producePrompt(left + ' more characters required','message-error','red');
  return false;
}

producePrompt('Valid', 'message-error', 'green');
setTimeout(function(){jsHide('message-error');}, 1000);
return true;

}

function validateForm() {
    if (!validateName() || !validatePhone() || !validateEmail() || !validateMessage()) {
        jsShow('submitErrorMessage');
        producePrompt('Please fix errors to submit.', 'submitErrorMessage', 'red');
        setTimeout(function(){jsHide('submitErrorMessage');}, 2000);
        return false;
    }
    else {
        console.log("Submiting form")
        return true;
    }
}

function jsShow(id) {
    document.getElementById(id).style.display = 'block';
}

function jsHide(id) {
    document.getElementById(id).style.display = 'none';
}


function producePrompt(message, promptLocation, color) {

document.getElementById(promptLocation).innerHTML = message;
document.getElementById(promptLocation).style.color = color;
document.getElementById(promptLocation).style.display = 'block';
}

function after_form_submitted(data){
        if(data == 'OK')
        {
            $('#submitSuccessMessage div').text('Form Sent Successfully');
            $('#submitSuccessMessage').show();
            $('#submitErrorMessage').hide();
        }
        else
        {
            $('#submitErrorMessage div').text('<ul>Could not Send form</ul>');
            $('#submitSuccessMessage').hide();
            $('#submitErrorMessage').show();

        }

        //stop spamming a bit
        $('button[type="button"]', $form).each(function()
        {
            $(this).hide();
        });
    }

$('#contactForm').submit(function(e) {
  e.preventDefault();

  $form = $(this);


  if(validateForm()){

    //show some response on the button
    $('button[type="submit"]', $form).each(function()
    {
        $btn = $(this);
        $btn.prop('type','button' );
        $btn.prop('orig_label',$btn.text());
        $btn.text('Sending ...');
    });
    
    $.ajax({
        type: "POST",
        url: "../form_submit/",
        data: $form.serialize(),
        success: after_form_submitted("OK"),
        error: function (jqXHR, exception) {
            var msg = '';
            if (jqXHR.status === 0) {
                msg = 'Not connect.\n Verify Network.';
            } else if (jqXHR.status == 404) {
                msg = 'Requested page not found. [404]';
            } else if (jqXHR.status == 500) {
                msg = 'Internal Server Error [500].';
            } else if (exception === 'parsererror') {
                msg = 'Requested JSON parse failed.';
            } else if (exception === 'timeout') {
                msg = 'Time out error.';
            } else if (exception === 'abort') {
                msg = 'Ajax request aborted.';
            } else {
                msg = 'Uncaught Error.\n' + jqXHR.responseText;
            }
            after_form_submitted("NOK");
        },
        dataType: 'json'
    });
  }

});


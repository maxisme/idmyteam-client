$(document).ready(function(){
    $('#password').parent().css('display', 'none');
    $('#confirm').parent().css('display', 'none');
    $('#permission').change(function(){
        if($(this).val() == 0){
            $('#password').parent().css('display', 'none');
            $('#confirm').parent().css('display', 'none');
        }else{
            $('#password').parent().css('display', '');
            $('#confirm').parent().css('display', '');
        }
    });
});
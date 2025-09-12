$(document).ready(function () {
    // The main form submission is now handled by the fetch API in index.html,
    // so we can simplify the do_login click handler.
    $("#do_login").click(function () {
        closeLoginInfo();
        // The rest of the validation logic is now handled by the server-side form validation.
    });

    // Reset previously results and hide all message on .keyup()
    $("#login_form input").keyup(function () {
        $(this).parent().find('span').css("display", "none");
    });
});

function openLoginInfo() {
    $('.b-form').css("opacity", "0.01");
    $('.box-form').css("left", "-37%");
    $('.box-info').css("right", "-37%");
}

function closeLoginInfo() {
    $('.b-form').css("opacity", "1");
    $('.box-form').css("left", "0px");
    $('.box-info').css("right", "-5px");
}
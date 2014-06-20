/*jslint browser: true*/
/*globals $*/

$(document).ready(function () {
    "use strict";
    $("a.lang").click(function (e) {
        e.preventDefault();
        $("form.langchooser").submit();
    });
});


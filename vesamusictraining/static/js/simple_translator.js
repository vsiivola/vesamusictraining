/*jslint
  browser: true,
  sub: true
*/
/*globals lang, unescape, $*/

// Parse lang

if (typeof lang === 'undefined') { var lang = "fi";}
// See if we pass the lang in from the url
var result = new RegExp("lang=([^&]*)", "i").exec(window.location.search);
if (result) {
    lang =  unescape(result[1]);
}

function insert_langchooser() {
    "use strict";
    if (!firstlangchooser) {
        return;
    }
    firstlangchooser = false;
    var langimages;
    if (lang === "fi") {
        langimages = $('<li class="langchooser"><img src="/static/generated_assets/images/gb.png" /></li>');
        langimages.click(function () {
            window.location.href = window.location.href.substring(0, window.location.href.indexOf('&')) + "?lang=en";
        });
    } else {
        langimages = $('<li class="langchooser"><img src="/static/generated_assets/images/fi.png" /></li>');
        langimages.click(function () {
            window.location.href = window.location.href.substring(0, window.location.href.indexOf('&')) + "?lang=fi";
        });
    }

    $("ul.navbar-nav").append(langimages);
}

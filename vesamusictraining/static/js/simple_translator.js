/*jslint
   sub: true
*/
/*globals lang, window, unescape, $*/
// Parse lang

if (typeof lang === 'undefined') { var lang = "fi";}
// See if we pass the lang in from the url
var result = new RegExp("lang=([^&]*)", "i").exec(window.location.search);
if (result) {
    lang =  unescape(result[1]);
}
var firstrun = true;
var firstbasetrans = true;
var firstlangchooser = true;

function get_transtable(pagename, language) {
    "use strict";
    var ttable = {};

   // global translation strings
    if  ( language === "fi") {
        ttable["Home"] = "Koti";
    }

    if (pagename === "basepage" && firstbasetrans) {
        firstbasetrans = false;
        if (language === "fi") {
            ttable["Sign out"] = "Kirjaudu ulos";
            ttable["Sign in"] = "Kirjaudu sisään";
            ttable["Contact"] = "Ota yhteyttä";
            ttable["News"] = "Uutiset";
            ttable["Music training"] = "Musiikinharjoittelu";
            return ttable;
        }
        return null;
    }

    if (pagename === "indexpage") {
        if (language === "fi") {
            ttable["Please sign in"] = "Kirjaudu sisään";
            ttable["sign up"] = "luo_tunnus";
            ttable["or"] = "tai";
            ttable["Welcome"] = "Astu sisään";
            ttable["This is a simple app for improvings skills to hear different musical constructs and to read the corresponding musical notation."] = "Tämä on yksinkertainen harjoitus, jonka tarkoituksena on opettaa kuulemaan erilaisia musiikillisia rakenteita ja tunnistamaan niitä vastaava nuotinnos."
            return ttable;
        }
        return null;
    }

    if (pagename === "chooserpage") {
        if (language === "fi") {
            ttable["Music Training | Choose your exercise"] = "Musiikinharjoittelu | Valitse harjoitus";
            ttable["version"] = "versio";
            ttable["completed"] = "tehty";
            ttable["score"] = "pisteet";
            ttable["on"] = "";
            ttable["More information"] = "Lisätietoja";
            ttable["Enter"] = "Aloita";
            ttable["exercises"] = "harjoitusta";
            ttable["Hints"] = "Ohjeita";
            ttable["Exercise information"] = "Tietoja harjoituksesta"
            return ttable;
        }
        return null;
    }

    if (pagename === "exercisepage") {
        if (language === "fi") {
            ttable["Music Training"] = "Musiikinharjoittelu";
            ttable["Play"] = "Soita";
            return ttable;
        }
        return null;
    }

    if (pagename === "resultpage") {
        if (language === "fi") {
            ttable["Music Training | Results"] = "Musiikinharjoittelu | Tulokset";
            ttable["Continue"] = "Jatka";
            return ttable;
        }
        return null;
    }

    if (pagename === "loginpage") {
        if (language === "fi") {
            ttable["Username"] = "Käyttäjätunnus";
            ttable["Sign in"] = "Kirjaudu sisään";
            ttable["Sorry, that's not a valid username or password"] = "Väärä tunnus tai salasana";
            ttable["Password"] = "Salasana";
            return ttable;
        }
        return null;
    }

    if (pagename === "logoutpage") {
        if (language === "fi") {
            ttable["Sign out"] = "Kirjaudu ulos";
            ttable["You have succesfully signed out"] = "Olet kirjautunut ulos";
            return ttable;
        }
        return null;
    }

    if (pagename === "regformpage") {
        if (language === "fi") {
            ttable["Register"] = "Luo käyttäjätunnus";
            ttable["Username:"] = "Käyttäjätunnus";
            ttable["E-mail:"] = "Sähköpostiosoite:";
            ttable["Password:"] = "Salasana:";
            ttable["Password (again):"] = "Salasana (uudestaan):";
            ttable["Submit"] = "Lähetä";
            ttable["Enter a valid email address."] = "Anna toimiva sähköpostiosoite";
            return ttable;
        }
        return null;
    }

    if (pagename=="newspage") {
        if (language=="fi") {
            ttable["News"] = "Uutiset";
            return ttable;
        }
        return null;
    }
}

function translate_page(pagename, language) {
    "use strict";
    var transtable = get_transtable(pagename, language);

    real_translate_page(transtable);
}

function real_translate_page(transtable) {
    "use strict";
    if (transtable) {
        $(".localizestring").each(function () {
            var newtext = transtable[$(this).text()];
            if (newtext) {
                $(this).html(newtext);
            }
        });

        $("input.ui-button").each(function () {
            var t = transtable[$(this).val()];
            if (t) {
                $(this).val(t);
            }
        });
    }
    append_lang();
}

function append_lang() {
    "use strict";
    // Rewrite all links to use lang parameter
    if (firstrun) {
        firstrun = false;
        $('a').each(function () {
            this.href += (/\?/.test(this.href) ? '&' : '?') + 'lang=' + lang;
        });
        if (! typeof transtable === 'undefined') {
            $("input.ui-button").each(function () {
                var t = transtable[$(this).val()];
                if (t) {
                    $(this).val(t);
                }
            });
        }
    }
}

function Translator(pagename, language) {
    "use strict";
    this.transtable = get_transtable(pagename, language);
    var transtable = this.transtable;

    this.translate_page = function () {
        real_translate_page(this.transtable);
    };

    if (this.transtable) {
        this.tp = function (phrase) {
            var t = this.transtable[phrase];
            if (t) {
                return this.transtable[phrase];
            }
            return phrase;
        };

        this.translate_form = function () {
            $("label").each(function () {
                var t = transtable[$(this).text()];
                if (t) {
                    $( this ).html(t);
                }
            });

            $("input").each(function () {
                var t = transtable[$(this).val()];
                if (t) {
                    $(this).val(t);
                }
            });

            $("li").each(function () {
                var t = transtable[$(this).text()];
                if (t) {
                    $(this).html(t);
                }
            });
        };
    } else {
        this.tp = function (phrase) {
            return phrase;
        };
        this.translate_form = function () { };
    }
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

    $("ul.headerlist").append(langimages);
}

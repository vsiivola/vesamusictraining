lang = "fi"

function get_transtable(pagename, language) {
    var ttable = {};
    
   // global translation strings
    if  (language=="fi") {
        ttable["Home"] = "Koti";
    }

    if (pagename=="basepage") {
        if (language=="fi") {
            ttable["Sign out"] = "Kirjaudu ulos";
            ttable["Sign in"] = "Kirjaudu sisään";
            ttable["Contact"] = "Ota yhteyttä";
            ttable["Music training"] = "Musiikinharjoittelu";
            return ttable;
        }
        return null
    }

    if (pagename=="indexpage") {
        if (language=="fi") {
            ttable["Please sign in"] = "Kirjaudu sisään";
            ttable["sign up"] = "luo_tunnus";
            ttable["or"] = "tai";
            return ttable;
        }
        return null;
    }

    if (pagename=="chooserpage") {
        if (language=="fi") {
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

    if (pagename=="loginpage") {
        if (language=="fi") {
            ttable["Username"] = "Käyttäjätunnus";
            ttable["Sign in"] = "Kirjaudu sisään";
            ttable["Sorry, that's not a valid username or password"] = "Väärä tunnus tai salasana";
            ttable["Password"] = "Salasana";
            return ttable;
        }
        return null;
    }

    if (pagename=="regformpage") {
        if (language=="fi") {
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
}

function translate_page(pagename, language) {
    var transtable = get_transtable(pagename, language);

    real_translate_page(transtable);
}

function real_translate_page(transtable) {
    if (transtable) {
        $(".localizestring").each(function() {
            $( this ).html(transtable[$(this).text()]);
        });
        $("input.ui-button").each(function() {
            var t = transtable[$(this).val()]
            if (t) {
                $(this).val(t);
            }
        });
    }
}

function Translator(pagename, language) {
    this.transtable = get_transtable(pagename, language);
    var transtable = this.transtable;

    this.translate_page = function() { real_translate_page(this.transtable); }

    if (this.transtable) {
        this.tp = function(phrase) {
            return this.transtable[phrase];
        }

        this.translate_form = function() {
            $("label").each(function() {
                $( this ).html(transtable[$(this).text()]);
            });

            $("input").each(function() {
                var t = transtable[$(this).val()]
                if (t) {
                    $(this).val(t);
                }
            });

            $("li").each(function() {
                var t = transtable[$(this).text()]
                if (t) {
                    $(this).html(t);
                }
            });
        }
    } else {
        this.tp = function(phrase) {
            return phrase;
        }
        this.translate_form = function() { }
    }
}

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
            //ttable["Enter"] = "Aloita";
            ttable["exercises"] = "harjoitusta";
            ttable["Hints"] = "Ohjeita";
            ttable["Exercise information"] = "Tietoja harjoituksesta"
            return ttable;
        }
        return null;
    }

}

function translate_page(pagename, language) {
    var transtable = get_transtable(pagename, language);

    if (transtable) {
        $(".localizestring").each(function() {
            $( this ).html(transtable[$(this).text()]);
        });
    }
}

function Translator(pagename, language) {
    this.transtable = get_transtable(pagename, language);
    
    if (this.transtable) {
        this.tp = function(phrase) {
            return this.transtable[phrase];
        }
    } else {
        this.tp = function(phrase) {
            return phrase;
        }
    }
}

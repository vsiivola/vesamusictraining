/*globals Translator, lang, $*/

var nt = new Translator("newspage", lang);

function showNews(newsroot) {
    "use strict";
    var newshead = $('<div class="container"><h1>' + nt.tp("News") + "</h1></div>");

    newsroot.append(newshead);

    $.get('/news/list_news/' + lang, null, function (response) {
        var newslist = JSON.parse(response),
            i,
            newsitem,
            datestring,
            fullstring,
            nis;

        for (i = 0; i < newslist.length; i += 1) {
            newsitem = newslist[i];

            if (lang === "fi") {
                datestring = String(newsitem.day) + "." + newsitem.month + "." + newsitem.year;
            } else {
                datestring = String(newsitem.month) + "/" + newsitem.day + "/" + newsitem.year;
            }

            fullstring = '<h4>' + datestring + " " + newsitem.title + "</h4>"
                + '<p>' + newsitem.content + "</p></div>";
            nis = $(fullstring);
            newshead.append(nis);
        }
    });
}

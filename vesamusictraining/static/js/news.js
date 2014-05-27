/*globals Translator, lang, $*/

var nt = new Translator("newspage", lang);

function showNews(newsroot) {
    "use strict";
    var newstable = $("<table bgcolor=\"eeeeee\" width=\"100%\" />"),
        newshead = $("<tr><td><h3>" + nt.tp("News") + "</h3></td></tr>");
    newsroot.append(newstable);
    newstable.append(newshead);

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

            fullstring = "<tr><td style=\"padding-right: 10px;\">" + datestring + "</td><td><h4>" + newsitem.title + "</h4></td></tr>";
            fullstring += "<tr><td /><td>" + newsitem.content + "</td></tr>";
            nis = $(fullstring);
            newstable.append(nis);
        }
    });
}

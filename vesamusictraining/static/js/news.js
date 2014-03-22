nt = new Translator("newspage", lang);

function showNews(newsroot) {
    var newshead = $("<h3>" + nt.tp("News") + "</h3>")
    var newstable = $("<table bgcolor=\"eeeeee\" />");
    newsroot.append(newshead);
    newsroot.append(newstable);

    $.get('/news/list_news', null, function(response) {
        var newslist = JSON.parse(response);
        
        for (var i=0; i<newslist.length; i++) {

            var newsitem = newslist[i];

            if (lang == "fi") {
                datestring = ""+newsitem.day+"."+newsitem.month+"."+newsitem.year;
            }

            fullstring = "<tr><td style=\"padding-right: 10px;\">"+datestring+"</td><td><h4>"+newsitem.title+"</h4></td></tr>"
            fullstring += "<tr><td /><td>"+newsitem.content+"</td></tr>"
            nis = $(fullstring)
            
            newsroot.append( nis );
            
        }

    });
}

nt = new Translator("newspage", lang);

function showNews(newsroot) {
    var newstable = $("<table bgcolor=\"eeeeee\" width=\"100%\" />");
    newsroot.append(newstable);

    var newshead = $("<tr><td><h3>" + nt.tp("News") + "</h3></td></tr>")
    newstable.append(newshead);

    $.get('/news/list_news/'+lang, null, function(response) {
        var newslist = JSON.parse(response);
        
        for (var i=0; i<newslist.length; i++) {

            var newsitem = newslist[i];

            if (lang == "fi") {
                datestring = ""+newsitem.day+"."+newsitem.month+"."+newsitem.year;
            } else {
                datestring = ""+newsitem.month+"/"+newsitem.day+"/"+newsitem.year;
            }

            fullstring = "<tr><td style=\"padding-right: 10px;\">"+datestring+"</td><td><h4>"+newsitem.title+"</h4></td></tr>"
            fullstring += "<tr><td /><td>"+newsitem.content+"</td></tr>"
            nis = $(fullstring)
            
            newstable.append( nis );
            
        }

    });
}

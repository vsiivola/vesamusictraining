ct = new Translator("chooserpage", lang);

function ChooserScreen(mainWindow) {
    this.mainWindow = mainWindow;
    this.course_list =  [];

    this.render_full = function() {
        $("#maintitle").html(ct.tp("Music Training | Choose your exercise"));
            
        var clist = this.course_list.lectures;
        var tstring = '<div id="courses" class="ui-accordion">';
        
        lclist = []
        j = 0
        for (var i=0; i<clist.length; i++) {
            var lecture = clist[i]
            if (lecture.language != lang)
               continue;
            lclist.push(lecture)
            tstring += '<h3 class="ui-accordion-header'
            if (lecture.complete)
                tstring += ' inactive-lecture'
            tstring += '"><a href="#">'+lecture.title+'</a></h3>';
            tstring += '<div id="acc' +j + '" class="ui-accordion-content">';
            if (lecture.instructions)
                tstring += '<H3>'+ct.tp("Hints")+'</H3><p>'+lecture.instructions+'</p>';

            if (lecture.outside_info_name) {
                tstring += '<H3>'+ct.tp("More information")+'</H3>'+'<a class="outside" href="' + 
                    lecture.outside_info_link +
                    '"> ' + lecture.outside_info_name + "</a>"
            }

            tstring += '<H3>' + ct.tp("Exercise information") + '</H3>'
            tstring += '<ul class="lecture_info">';
            tstring += '<li> version ' +  lecture.version + '</li>';
            tstring += '<li> ' +  lecture.num_exercises + ' '+ct.tp("exercises")+'</li>';
            if (lecture.complete) {
                tstring += '<li>'+ct.tp("completed")+'<ul>';
                tstring += '<li>'+ct.tp("version")+' ' + lecture.version + '</li>';
                tstring += '<li>'+ct.tp("score")+' ' + lecture.score + '</li>';
                tstring += '<li>'+ct.tp("on")+' ' + lecture.complete_date + "</li></ul>";
            }
            tstring += '</ul>';
            tstring += '</div>';
            j=j+1
        }
        tstring += "</div>";
        $("div#main").html(tstring);
        //$("div#main").slideDown("slow");
     
        for (var i=0; i<lclist.length; i++) {
            var myDiv = document.getElementById("acc"+i);
            var obj = document.createElement("input");
            obj.type = "button";
            obj.id = "btn"+i;
            obj.name = lclist[i].title
            obj.value = ct.tp("Enter");
            obj.className = "ui-button-text"
            obj.onclick = function() {
                that.mainWindow.course_name = this.name;
                that.mainWindow.exercise_index = 0;
                that.mainWindow.show.apply(that.mainWindow);
            }
            //obj.style ="float:right;"
            myDiv.appendChild(obj);
        }

        $("#courses").accordion();
        //$("div#main").slideDown("slow")
    }

    this.res = function(response) {
        this.course_list = JSON.parse(response);
        this.render_full()
    }

    this.get_server_info = function(foo, bar) {
        that = this; //preserve context for callback
        $.get(
            '/exercise/list_lectures', 
            null, 
            function(response) {that.res.apply(that, arguments);})

    }
}

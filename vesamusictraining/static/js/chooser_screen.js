lang = "fi"

if (lang == "fi") {
    maintitle_uistr = "Musiikinopettelu | Valitse harjoitus";
    version_uistr = "versio";
    completed_uistr = "tehty";
    score_uistr = "pisteet";
    on_uistr = "";
    moreinfo_uistr = "Lisätietoja";
    enter_uistr = "Aloita";
    exercises_uistr = "harjoitusta";
    instructions_uistr = "Ohjeita";
    lectinfo_uistr = "Tietoja harjoituksesta"
} else if (lang == "en") {
    maintitle_uistr = "Music Training | Choose your exercise";
    version_uistr = "version";
    completed_uistr = "completed";
    score_uistr = "score";
    on_uistr = "on";
    moreinfo_uistr = "More information";
    enter_uistr = "Enter";
    exercises_uistr = "exercises";
    instructions_uistr = "Hints";
    lectinfo_uistr = "Exercise information"
}


function ChooserScreen(mainWindow) {
    this.mainWindow = mainWindow;
    this.course_list =  [];

    //this.render_full = function() {
    //    var that2 = this
    //    $("div#main").slideUp("slow", function () {that2.real_render.apply(that2);})
    //}

    this.render_full = function() {
        $("#maintitle").html(maintitle_uistr);
            
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
                tstring += '<H3>'+instructions_uistr+'</H3><p>'+lecture.instructions+'</p>';

            if (lecture.outside_info_name) {
                tstring += '<H3>'+moreinfo_uistr+'</H3>'+'<a class="outside" href="' + 
                    lecture.outside_info_link +
                    '"> ' + lecture.outside_info_name + "</a>"
            }

            tstring += '<H3>' + lectinfo_uistr + '</H3>'
            tstring += '<ul class="lecture_info">';
            tstring += '<li> version ' +  lecture.version + '</li>';
            tstring += '<li> ' +  lecture.num_exercises + ' '+exercises_uistr+'</li>';
            if (lecture.complete) {
                tstring += '<li>'+completed_uistr+'<ul>';
                tstring += '<li>'+version_uistr+' ' + lecture.version + '</li>';
                tstring += '<li>'+score_uistr+' ' + lecture.score + '</li>';
                tstring += '<li>'+on_uistr+' ' + lecture.complete_date + "</li></ul>";
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
            obj.value = enter_uistr;
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

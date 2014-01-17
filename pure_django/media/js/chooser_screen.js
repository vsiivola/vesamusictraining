function ChooserScreen(mainWindow) {
    this.mainWindow = mainWindow;
    this.course_list =  [];

    //this.render_full = function() {
    //    var that2 = this
    //    $("div#main").slideUp("slow", function () {that2.real_render.apply(that2);})
    //}

    this.render_full = function() {
        $("#maintitle").html("Music Training | Choose your exercise");
        var clist = this.course_list.lectures;
        var tstring = '<div id="courses" class="ui-accordion">';
        for (var i=0; i<clist.length; i++) {
            var lecture = clist[i]
            tstring += '<h3 class="ui-accordion-header'
            if (lecture.complete)
                tstring += ' inactive-lecture'
            tstring += '"><a href="#">'+lecture.title+'</a></h3>';
            tstring += '<div id="acc' +i + '" class="ui-accordion-content">';
            tstring += '<ul class="lecture_info">';
            tstring += '<li> version ' +  lecture.version + '</li>';
            tstring += '<li> ' +  lecture.num_exercises + ' exercises</li>';
            if (lecture.complete) {
                tstring += '<li>completed<ul>';
                tstring += '<li>version ' + lecture.version + '</li>';
                tstring += '<li>score ' + lecture.score + '</li>';
                tstring += '<li>on ' + lecture.complete_date + "</li></ul>";
            }
            if (lecture.outside_info_name) {
                tstring += '<li>More info: <a class="outside" href="' + 
                    lecture.outside_info_link +
                    '"> ' + lecture.outside_info_name + "</a>"
            }
            tstring += '</ul>';
            //tstring += '<p>This is the description of the exercise.</p>';
            tstring += '</div>';
        }
        tstring += "</div>";
        $("div#main").html(tstring);
        //$("div#main").slideDown("slow");
     
        for (var i=0; i<clist.length; i++) {
            var myDiv = document.getElementById("acc"+i);
            var obj = document.createElement("input");
            obj.type = "button";
            obj.id = "btn"+i;
            obj.name = clist[i].title
            obj.value = "Enter";
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

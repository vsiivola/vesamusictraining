lang = "fi"

if (lang=="fi") {
    maintitle_resuistr = "Musiikinopettelu | Tulokset"
    continue_uistr = "Jatka"
} else if (lang=="en") {
    maintitle_resuistr = "Music Training | Results"
    continue_uistr = "Continue"
}

function ResultScreen(mainWindow) {
    this.mainWindow = mainWindow
    that = this

    this.get_server_info = function () {
        that = this
        $("span").removeClass("ui-icon-circle-check");
        $("span").removeClass("ui-icon-circle-close");
        $("span").css("opacity", "0.0");

        $("div#main").slideUp("slow", function () {that.get_server_info2.apply(that);})
    }

    this.get_server_info2 = function(foo, bar) { // not really getting any info nowsen
        $("#maintitle").html(maintitle_resuistr);
        var mdiv = $("div#main");
        mdiv.html(
                  '<div class="results ui-corner-all">'+ that.mainWindow.correct_clicks + " / " + that.mainWindow.num_exercises +"</div>");

        $.get(that.mainWindow.course_name+'/complete/', {
            'num_correct': JSON.stringify(that.mainWindow.correct_clicks)},
              function () {
                  var obj = document.createElement("input");
                  obj.type = "button";
                  obj.value = continue_uistr;
                  obj.className = "ui-button-text"
                  obj.onclick = function () {
                      that.mainWindow.course_name = null;
                      that.mainWindow.exercise_index = 0;
                      that.mainWindow.show.apply(that.mainWindow);
                  }
                  mdiv.append(obj);
                  $("div#main").slideDown("slow");
              });
    }
}

/*globals ChooserScreen, ExerciseScreen, ResultScreen, insert_langchooser*/

function MainController() {
    "use strict";

    this.course_name = null;
    var chooser_screen = new ChooserScreen(this),
        exercise_screen = new ExerciseScreen(this),
        result_screen = new ResultScreen(this),
        lchooser_shown = false;

    this.show = function () {
        var m_screen;
        if (this.course_name === null) {
            //render chooser screen
            m_screen = chooser_screen;
            this.exercise_index = 0;
            this.num_exercises = 1;
            this.correct_clicks = 0;
        } else if (this.exercise_index < this.num_exercises) {
            m_screen = exercise_screen;
        } else {
            m_screen = result_screen;
        }
        //$("div#debug").html(this.course_name + " " + this.exercise_index + " " + this.num_exercises + " " + this.exercise_index < this.num_exercises)
        m_screen.get_server_info(this.course_name, this.exercise_index);
        //if (!lchooser_shown) {
        //    lchooser_shown = true;
        //    insert_langchooser();
        //}
    };
}



function MainController() {
    this.course_name = null;
    var chooser_screen = new ChooserScreen(this);
    var exercise_screen = new ExerciseScreen(this);
    var result_screen = new ResultScreen(this);
    var m_screen = null;
    var lchooser_shown = false;

    this.show = function() {
        if (this.course_name == null) {
            //render chooser screen
            var m_screen = chooser_screen;
            this.exercise_index = 0;
            this.num_exercises = 1;
            this.correct_clicks = 0;
        } else if (this.exercise_index<this.num_exercises) {
            var m_screen = exercise_screen;
        } else {
            var m_screen = result_screen
        }
        //$("div#debug").html(this.course_name + " " + this.exercise_index + " " + this.num_exercises + " " + this.exercise_index < this.num_exercises)
        m_screen.get_server_info(this.course_name, this.exercise_index);
        if (! lchooser_shown) {
            lchooser_shown = true;
            insert_langchooser();
        } 
   }
}


# This script is modified from the official take_picture script provided
# by UIUC/VMD library. Some slight modification is made for our own purpose
# of making movie.
#
# Link:
#   http://www.ks.uiuc.edu/Research/vmd/script_library/scripts/trajectory_movie/
#
# Author: Andrew Dalke (dalke@ks.uiuc.edu)
# Modified By: Yunlong Liu (davislong198833@gmail.com)
#
# PROCEDURES:
#  make_trajectory_movie_files - generates by default one RGB image
#    per animation frame, using the renderer 'snapshot.'  To change
#    these default operations, change parameters in the call to
#    take_picture in the body of the procedure
#  take_picture - a general, multi-purpose routine for taking
#    VMD screen shots

proc take_picture {args} {
  global take_picture

  # when called with no parameter, render the image
  if {$args == {}} {
    set f [format $take_picture(format) $take_picture(frame)]
    # take 1 out of every modulo images
    if { [expr $take_picture(frame) % $take_picture(modulo)] == 0 } {
      render $take_picture(method) $f
      # call any unix command, if specified
      if { $take_picture(exec) != {} } {
        set f [format $take_picture(exec) $f $f $f $f $f $f $f $f $f $f]
        eval "exec $f"
       }
    }
    # increase the count by one
    incr take_picture(frame)
    return
  }
  lassign $args arg1 arg2
  # reset the options to their initial stat
  # (remember to delete the files yourself
  if {$arg1 == "reset"} {
    set take_picture(frame)  0
    set take_picture(format) "./temp.%05d.ppm"
    set take_picture(method) TachyonInternal
    set take_picture(modulo) 1
    set take_picture(exec)    {}
    return
  }
  # set one of the parameters
  if [info exists take_picture($arg1)] {
    if { [llength $args] == 1} {
      return "$arg1 is $take_picture($arg1)"
    }
    set take_picture($arg1) $arg2
    return
  }
  # otherwise, there was an error
  error {take_picture: [ | reset | frame | format  | \
  method  | modulo ]}
}
# to complete the initialization, this must be the first function
# called.  Do so automatically.
take_picture reset

proc make_trajectory_movie_files {step_size} {
  set num [molinfo top get numframes]
  # loop through the frames
  for {set i [expr {$step_size - 1}]} {$i < $num} {incr i $step_size} {
    # go to the given frame
    animate goto $i
    # force display update
    display update
    # take the picture
    take_picture
  }
}

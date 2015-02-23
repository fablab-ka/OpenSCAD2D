OpenSCAD2D
==========

OpenSCAD2D is a software for creating solid 2D CAD objects.

This Software is inspired by the ingenious 3D CAD Modeller [OpenSCAD](http://www.openscad.org/).

### Content

* General Information
    * [Dependencies](#Dependencies)
    * [Screenshots](#Screenshots)
    * [TODO](#TODO)
* [API](#API)
    * [Primitives](#Primitives)
        * [Circle](#Circle)
        * [Rectangle](#Rectangle)
        * [Path](#Path)
    * [Modifiers](#Modifiers)
        * [Translate](#Translate)
        * [Rotate](#Rotate)
        * [Scale](#Scale)
        * [Hull](#Hull)

#### Dependencies

* [pywatch](https://github.com/cmheisel/pywatch)
* [pyqt4](http://www.riverbankcomputing.co.uk/software/pyqt/intro) ([Installer](http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt4-4.11.3-gpl-Py2.7-Qt4.8.6-x32.exe))
* [pyparsing](http://pyparsing.wikispaces.com/Download+and+Installation)
* [shapely](https://pypi.python.org/pypi/Shapely#downloads)

### Screenshots

![Image of First Union](https://raw.githubusercontent.com/fablab-ka/OpenSCAD2D/master/docs/first_union.png)

### TODO

* [ ] Language
    * [x] ~~Single Line Comments~~
    * [x] ~~Multi Line Comments~~
    * [ ] Basic Calculations
    * [ ] Variable assignment & lookup
    * [ ] Math functions (cos sin tan acos asin atan atan2 abs ceil concat cross exp floor ln len let log lookup max min norm pow rands round sign sqrt)
    * [ ] Datatypes
        * [x] ~~integer~~
        * [x] ~~float~~
        * [ ] boolean
        * [ ] string
    * [ ] Primitives
        * [x] ~~circle~~
        * [x] ~~rect~~
        * [ ] path
    * [ ] Attached Modifiers
        * [x] ~~translate~~
        * [x] ~~rotate~~
        * [x] ~~scale~~
        * [ ] Debugging Aids (% # ! *)
        * [ ] mirror
    * [ ] Scope Modifiers
        * [ ] translate
        * [ ] rotate
        * [ ] scale
        * [ ] hull
        * [ ] union
        * [ ] difference
        * [ ] intersection
        * [ ] assign
    * [ ] Modules
        * [ ] module definition
        * [ ] module call
        * [ ] module argument stack evaluation
    * [ ] Advanced Structures
        * [ ] if/else statement
        * [ ] basic loop
        * [ ] include statements
* [ ] Application Frame
    * [x] ~~auto reload file~~
    * [x] ~~commandline argument~~
    * [ ] main menu 
        * [ ] load file 
        * [ ] exit
        * [ ] about
        * [ ] help


API
===

The following documentation describes the statements and modifiers that are possible to use with OpenScad2D.

## Primitives

### Circle

```OpenSCAD
circle( <radius>, [<resolution>] );
circle( r=<radius>, [$fn=<resolution>] );
circle( radius=<radius>, [$fn=<resolution>] );
```

### Rectangle

```OpenSCAD
rect( <width>, <height>] );
rect( w=<width>, h=<height>] );
rect( width=<width>, height=<height>] );
```

### Path

Not yet implemented!

```OpenSCAD
path( <x1>, <y1>, <x2>, <y2>, ... );
```


## Modifiers

Modifiers can be written in the form:

```OpenSCAD
translate(5, 10)
rect(10, 10);
```

or as a modifier scope

```OpenSCAD
translate(5, 10) {
  rect(10, 10);

  circle(30);
}
```

### Translate

```OpenSCAD
translate( <x>, <y> );
translate( x=<x>, y=y );
```

### Rotate

```OpenSCAD
rotate( <angle>, [<origin x>], [<origin y>], [<use radian>] );
rotate( a=<angle>, [x=<origin x>], [y=<origin y>], [rad=<use radian> );
rotate( angle=<angle>, [xorigin=<origin x>], [yorigin=<origin y>], [use_radian=<use radian> );
```

### Scale

```OpenSCAD
scale( <x>, <y> );
scale( x=<x>, y=y );
```

### Hull

TBD

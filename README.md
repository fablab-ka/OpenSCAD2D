[![Travis CI](https://api.travis-ci.org/fablab-ka/OpenSCAD2D.png)](https://travis-ci.org/fablab-ka/OpenSCAD2D)
[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/fablab-ka/openscad2d/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

OpenSCAD2D
==========

[![Flattr this git repo](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=fablab&url=https%3A%2F%2Fgithub.com%2Ffablab-ka%2FOpenSCAD2D&title=OpenSCAD2D&language=&tags=github&category=software)



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
    * [Scope Modifiers](#Scope Modifiers)
        * [Translate](#Translation Scope)
        * [Rotate](#Rotation Scope)
        * [Scale](#Scale Scope)
        * [Hull](#Hull Scope)
        * [Union](#Union)
        * [Difference](#Difference)
        * [Intersection](#Intersection)

#### Dependencies

* [Python 2.6 / Python 2.7](https://www.python.org/downloads/)
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
    * [x] ~~Basic Calculations~~
    * [ ] Variable assignment & lookup
    * [ ] Math functions (cos sin tan acos asin atan atan2 abs ceil concat cross exp floor ln len let log lookup max min norm pow rands round sign sqrt)
    * [ ] print statement
    * [ ] Datatypes
        * [x] ~~integer~~
        * [x] ~~float~~
        * [x] ~~boolean~~
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
        * [x] ~~union~~
        * [x] ~~difference~~
        * [x] ~~intersection~~
        * [ ] combine
        * [ ] knapsack
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

Modifiers influence the following statement

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

### Simplify
Produces a simplified geometry using the Douglas-Puecker algorithm.
Coordinates of the simplified geometry will be no more than the tolerance distance from the original. 
Unless the topology preserving option is used, the algorithm may produce self-intersecting or otherwise invalid geometries.

```OpenSCAD
simplify(1, False)
circle(30);
```


## Scope Modifiers

Scope Modifiers influence all it's child statements.


### Translation Scope

```OpenSCAD
translate(5, 10) {
  rect(10, 10);

  circle(30);
}
```

### Rotation Scope

```OpenSCAD
rotate(45) {
  rect(10, 10);

  circle(30);
}
```

### Scale Scope

```OpenSCAD
scale(1, 2) {
  rect(10, 10);

  circle(30);
}
```

### Hull Scope

```OpenSCAD
hull() {
  rect(10, 10);

  circle(30);
}
```

### Union

```OpenSCAD
union() {
  rect(10, 10);

  circle(30);
}
```

### Difference

```OpenSCAD
difference() {
  rect(10, 10);

  circle(30);
}
```

### Intersection

```OpenSCAD
intersection() {
  rect(10, 10);

  circle(30);
}
```
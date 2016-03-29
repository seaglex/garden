package main

import (
	"fmt"
	"reflect"
)

type Foo struct {
	V int
	x int
	S string
	e string
}

func (self *Foo) Error() string {
	return fmt.Sprint("Error of Foo:", self.V, self.x, self.S, self.e)
}

func Manipulate(x interface{}) reflect.Value {
	val := reflect.ValueOf(x)
	if val.Kind() == reflect.Ptr {
		fmt.Println("It's a ref, can set?", val.CanSet())
		val = val.Elem()
	} else {
		fmt.Println("It's not a ref, can set?", val.CanSet())
	}
	for n := 0; n < val.NumField(); n++ {
		f := val.Field(n)
		if f.CanSet() {
			if f.Kind() == reflect.Int {
				nVal := f.Int() + 1
				f.SetInt(nVal)
			}
			if f.Kind() == reflect.String {
				f.SetString(f.String() + "_m")
			}
		} else {
			fmt.Println("can't set")
		}
	}
	return val
}

func ValueOfRef() {
	foo := Foo{V: 1, x: 1, S: "string", e: "private_string"}
	fmt.Println("value=", foo)
	fmt.Println(Manipulate(foo).Interface())
	fmt.Println("ref=", &foo)
	fmt.Println(Manipulate(&foo).Interface())
	fmt.Println(&foo)
	fmt.Println(Manipulate(&Foo{S: "tmp_string", e: "tmp_private_string"}).Interface())
}

func main() {
	ValueOfRef()
}

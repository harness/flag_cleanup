// Simple flag cleanup in conditional
f2();

// Assignment cleanup
var a = doSomething("OTHER_FLAG");
if(a) {
    f1();
} else {
    f2();
}

if(f1()) {
    f1()
} else {
    f2()
}

// Complex cleanup
var c = f2();

function doSomething(flagName) {
    console.log(flagName)
    return true
}
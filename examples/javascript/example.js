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
var c = isEnabled("OTHER_FLAG") ? f3() : f4();

function doSomething(flagName) {
    console.log(flagName)
    return true
}

// Simple flag cleanup in conditional
if(isEnabled("STALE_FLAG")) {
    f1();
} else {
    f2();
}

// Assignment cleanup
var a = doSomething("OTHER_FLAG");
if(a) {
    f1();
} else {
    f2();
}

// function cleanup
function b() {
    return isToggleDisabled("STALE_FLAG");
}

if(b() || f1()) {
    f1()
} else {
    f2()
}

// Complex cleanup
var c = isToggleDisabled("STALE_FLAG") ? f1() : doSomething("STALE_FLAG") ? f2() : isEnabled("OTHER_FLAG") ? f3() : f4();

function doSomething(flagName) {
    console.log(flagName)
    return true
}
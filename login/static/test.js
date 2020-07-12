function myFunc(vars) {
    return vars
}

function myFunction(vars) {

  for (var key in vars) {
    var x = document.createElement("INPUT");
    x.setAttribute("type", "text");
    x.setAttribute("value", vars[key]["cname"]);
    document.body.appendChild(x);
  }

}

function formatCodePi(text){
	let arraytext = text.split("\n");
	let arrayresult = arraytext.filter(function (value, index){
		return (index%2 == 0);
	});
	textresult = arrayresult.join("\n");
	console.log(textresult);
}
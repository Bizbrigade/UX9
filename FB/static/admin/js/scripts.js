function getCurrentYear(element_id){
    const d = new Date();
    let year = d.getFullYear();
    console.log(year);
    document.getElementById(element_id).innerHTML=year;
}
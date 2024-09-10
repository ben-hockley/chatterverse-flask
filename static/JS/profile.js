allFollowButtons = document.querySelectorAll('.followButton');

for (let i=0; i < allFollowButtons.length; i++) {
    allFollowButtons[i].addEventListener('mouseover', function(){
        allFollowButtons[i].style.backgroundColor = 'green';
        allFollowButtons[i].innerHTML = 'Follow +';
    })
    allFollowButtons[i].addEventListener('mouseout', function(){
        allFollowButtons[i].style.backgroundColor = '#0D6EFD'; // bootstrap primary (blue)
        allFollowButtons[i].innerHTML = 'Follow';
    })
}
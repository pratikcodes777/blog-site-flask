// function like(postId) {
//   const likeCount = document.getElementById(`likes-count-${postId}`);
//   const likeButton = document.getElementById(`like-button-${postId}`);

//   fetch(`/like/${postId}`, { method: "POST" })
//     .then((res) => res.json())
//     .then((data) => {
//         likeCount.innerHTML = data['likes'];
//         if (data['liked'] === true){
//             likeButton.className = 'fa-solid fa-heart';
//         }else{
//             likeButton.className = 'fa-regular fa-heart';
//         }
        
        

//     });


// }


function like(postId) {
    const likeCount = document.getElementById(`likes-count-${postId}`);
    const likeButton = document.getElementById(`like-button-${postId}`);
  
    fetch(`/like/${postId}`, { method: "POST" })
      .then((res) => res.json())
      .then((data) => {
          likeCount.textContent = data.likes;
          if (data.liked) {
            likeButton.className = 'fa-solid fa-heart';
             
          } else {
            likeButton.className = 'fa-regular fa-heart';
          }
      });
  }
  
# board-game-data-analysis
BGG(Board Game Geek) 데이터 분석

### 개발 일지
**2020.09.28**
- [BoardGameGeek](https://boardgamegeek.com/) 크롤링
- 게임 데이터 1208페이지 수집 (약 1208*100개의 게임)
- 수집한 정보
  1. rank: 게임 랭크
  2. link: 게임 상세 페이지 링크
  3. thumbnail: 섬네일 링크 (NULL)
  4. title: 보드 게임 이름
  5. year: 보드 게임 출시 연도 (NULL)
  6. description: 보드 게임 설명 (NULL)
  7. geek_rating: Geek Rating. 자체적으로 보정된 평점
  8. avg_rating: Avg Rating
  9. num_voters: Num Voters
- 수집한 정보를 JSON 형식으로 저장하며, 100개의 페이지 단위로 나누어서 파일로 저장한다.
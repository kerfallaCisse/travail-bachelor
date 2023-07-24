# Rasa knowledge graph bot

Construction d'un chat bot connecté à un graphe de connaissances avec la framework Rasa Open Source.

Ce travail a été réalisé dans le cadre de mon travail de bachelor en Système d'information et science des services à l'université de Genève.

## But du chatbot

Le but du chatbot est de renseigner les utilisateurs sur les restaurants en Suisse. Le chatbot peut répondre aux questions suivantes :

* Donner la liste des restaurants en Suisse.
* Donner toutes les informations concernant un restaurant en mentionnant son nom ou en utilisant des mentions tels que le  *premier* , le  *deuxième* , etc. Le chatbot donne éventuellement les lieux qui sont proches d'un restaurant.
* Lister quelques curiosités qui sont autour d'un restaurant (précisement les terrains de jeux) se trouvant à une distance maximale de  *1km*.
* Lister les restaurants par type de cuisine dans une ville.
* Le chatbot peut éventuellement résoudre quelques ambiguïtés, par exemple lorsque plusieurs restaurants ont le même nom.

**NB**: utiliser des chiffres lorsque le chatbot utilise l'adverbe `combien`

**Important**: ***le chatbot devient intélligent à travers les questions posées par l'utilisateur. Par exemple lorsqu'il n'a pas encore parcouru les restaurants d'une ville ou les restaurants qui offrent certaines spécialités dans une ville.***

## Fonctionnement du chatbot

![1690199985591](image/README/1690199985591.png)

Cette figure illustre de manière simpliste le fonctionnement du chatbot.

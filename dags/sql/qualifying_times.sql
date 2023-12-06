    select q."q1",
        q."q2",
        q."q3",
        dr."driverId",
        r."year" - year(dr."dob") as age,
        cr."constructorId",
        cr."nationality",
        r."year",
        c."circuitId",
        lt.minLapTime
    from F1.QUALIFYING as q
    left join F1.DRIVERS as dr
        on (q."driverId" = dr."driverId")
    left join F1.CONSTRUCTORS as cr
        on (q."constructorId" = cr."constructorId")
    left join F1.RACES r
        on (q."raceId" = r."raceId")
    left join F1.CIRCUITS c
        on (r."circuitId"= c."circuitId")
    left join (
    select "driverId",
            "raceId",
            min("milliseconds")/1000 as minLapTime
        from F1.LAP_TIMES
        group by "driverId",
            "raceId"
    ) lt
    on (q."driverId" = lt."driverId"
        and q."raceId" = lt."raceId")
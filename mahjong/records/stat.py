# -*- coding: utf8 -*-
from __future__ import division

from django.contrib.auth.models import User
from records.models import Record, Player

from datetime import datetime

class Stat:
    user = None
    _plays = None
    _records = None
    _play_count = None
    year = None
    month = None
    valid = False

    def __init__(self, user, year=None, month=None):
        # set user
        self.user = user

        # set date
        self.year = year
        self.month = month

        if self.play_count() == 0:
            self.valid = False
            return
        else:
            self.valid = True

        # set stats
        self.set_stats()

    def plays(self):
        if not self.user:
            return None
        if not self._plays:
            plays = Player.objects.filter(user=self.user, record__valid=True)
            if self.year and self.month:
                to_year = self.year
                to_month = self.month + 1
                if to_month > 12:
                    to_month -= 12
                    to_year += 1
                plays = plays.filter(record__uploaded__gte=datetime(self.year, self.month, 1), record__uploaded__lt=datetime(to_year, to_month, 1))
            self._plays = plays
        return self._plays

    def play_count(self):
        if not self._play_count:
            self._play_count = len(self.plays())
        return self._play_count

    def records(self):
        if not self.user:
            return None
        if not self._records:
            records = self.user.records.filter(valid=True).distinct()
            if from_dt:
                records = records.filter(uploaded__gte=self.from_dt)
            if to_dt:
                records = records.filter(uploaded__lte=self.to_dt)
            self._records = records
        return self._records

    def set_stats(self):
        if not self.user:
            return

        # for winpoint
        point_sum = 0

        # for wincount
        win_count = 0

        # for rates
        _plus = 0
        _minus2 = 0
        _plus3 = 0
        _1 = 0
        _2 = 0
        _3 = 0
        _4 = 0
        for play in self.plays():
            point_sum += round(play.point / 1000, 2)

            if play.point >= 0:
                _plus += 1

            if play.rank == 1:
                # for rank 1
                uma = 20
                _1 += 1
                if play.record.match_type == 1:
                    win_count += 0.5
                else:
                    win_count += 1
            elif play.rank == 2:
                # for rank 2
                uma = 10
                _2 += 1
                if play.point < 0:
                    _minus2 += 1
            elif play.rank == 3:
                # for rank 3
                uma = -10
                _3 += 1
                if play.point >= 0:
                    _plus3 += 1
            elif play.rank == 4:
                # for rank 4
                uma = -20
                _4 += 1
            else:
                uma = 0

            if play.record.match_type == 1:
                uma = uma // 2
            point_sum += uma

        # set winpoint
        self.winpoint = point_sum
        self.winpoint_rate = round(point_sum / self.play_count(), 2)

        # set wincount
        self.wincount = win_count
        self.win_rate = round(self.wincount / self.play_count(), 2)

        # set rates
        self.percent_12 = round((_1 + _2) * 100 / self.play_count(), 2)
        self.percent_plus = round((_plus) * 100 / self.play_count(), 2)
        self.percent_minus2 = round((_minus2) * 100 / self.play_count(), 2)
        self.percent_plus3 = round((_plus3) * 100 / self.play_count(), 2)
        self.percent_4 = round((_4) * 100 / self.play_count(), 2)
        self.rank_rate = round((_1 + _2*2 + _3*3 + _4*4) / self.play_count(), 2)

        # set rank counts
        self.count_1 = _1
        self.count_2 = _2
        self.count_3 = _3
        self.count_4 = _4

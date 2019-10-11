import { Component, OnInit } from '@angular/core';
import {FormControl} from '@angular/forms';
import {Observable, from, timer} from 'rxjs';
import {map, startWith, debounce} from 'rxjs/operators';
import { MatFormFieldControl } from '@angular/material/form-field';


export interface Task {
  icon: string;
  name: string;
  platform: string; // TODO set possible values
  href: string;
}


@Component({
  selector: 'app-wuel-search-bar',
  templateUrl: './search-bar.component.html',
  styleUrls: ['./search-bar.component.css']
})
export class SearchBarComponent implements OnInit {
  private taskCtrl = new FormControl();
  private filteredTasks: Observable<Task[]>;
  private debounceTime = 250;

  // TODO get these from extra file to continously edit or something
  tasks: Task[] = [
    {
      // TODO have to emulate clicking for wuestudy, links are sadly non permanent
      name: 'Immatrikulationsbescheinigung',
      platform: 'wuestudy',
      icon: 'https://upload.wikimedia.org/wikipedia/commons/9/9d/Flag_of_Arkansas.svg',
      href: 'https://wuestudy.zv.uni-wuerzburg.de/qisserver/pages/cm/exa/enrollment/info/start.xhtml?_flowId=studyservice-flow&_flowExecutionKey=e1s2'
    },
    {
      name: 'Kurse',
      platform: 'wuecampus',
      icon: 'https://upload.wikimedia.org/wikipedia/commons/9/9d/Flag_of_Arkansas.svg',
      href: ''
    },
  ];

  private validTaskHref(): string {
    const taskFound = this.tasks.find(taskPred => taskPred.name === this.taskCtrl.value);
    if (taskFound) {
      // found so remove error and validate
      this.taskCtrl.setErrors({unknownTask: null});
      return taskFound.href;
    } else {
      // not found so false
      this.taskCtrl.setErrors({unknownTask: true});
      return null;
    }
  }

  constructor() {
    this.filteredTasks = this.taskCtrl.valueChanges
      .pipe(
        startWith(''),
        map(task => task ? this._filterTasks(task) : this.tasks.slice())
      );

    const debouncedValues = this.taskCtrl.valueChanges.pipe(debounce(() => timer(this.debounceTime)));
    debouncedValues.subscribe((task) => {
      this.validTaskHref();
    });

  }

  ngOnInit() {
  }

  onSubmit() {
    const valid = this.validTaskHref();
    if (valid) {
      window.open(valid, '_blank');
    }
  }

  private _filterTasks(value: string): Task[] {
    const filterValue = value.toLowerCase();
    return this.tasks.filter(task => task.name.toLowerCase().indexOf(filterValue) === 0);
  }
}

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommDataAccessComponent } from './comm-data-access.component';

describe('CommDataAccessComponent', () => {
  let component: CommDataAccessComponent;
  let fixture: ComponentFixture<CommDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

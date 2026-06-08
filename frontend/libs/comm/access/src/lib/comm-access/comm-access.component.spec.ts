import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CommAccessComponent } from './comm-access.component';

describe('CommAccessComponent', () => {
  let component: CommAccessComponent;
  let fixture: ComponentFixture<CommAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CommAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(CommAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
